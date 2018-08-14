import argparse
from typing import Callable, Dict, Optional

from easy_flags.fields import Field, MethodField


# will point to the latest defined config
CONFIG = None  # type: Optional[SimpleConfig]


class ConfigurationError(Exception):
    pass


class SimpleConfig(object):
    _desc = None

    def __init__(self, desc=None, strict=False, parser=None):
        self._attrs = self._get_attrs()
        self._resolvers = self._get_resolvers_map()
        self._define_map = {
            str: self._define_str,
            int: self._define_int,
            float: self._define_float,
            bool: self._define_bool,
        }
        conflict_handler = 'error' if strict else 'resolve'
        self._parser = parser or argparse.ArgumentParser(
            description=desc or self._desc, conflict_handler=conflict_handler
        )
        self._args = None
        self._defined = False

    def define(self):
        """
        Parse and define flags. This function should be called before using config object.
        """
        if self._defined:
            return self
        self._setup_arguments()
        self._parse_arguments()
        self._fill_attributes()
        globals()['CONFIG'] = self
        self._defined = True
        return self

    def print(self, title=None, block_size=39, prefix='|  '):
        """
        Pretty-print all flags.
        """
        if not self._defined:
            self.define()
        max_len = max([len(a) for a in self._attrs])
        print('+ ' + '- ' * block_size)
        if title:
            print(prefix + title)
        for a in self._attrs:
            key = a.ljust(max_len)
            value = getattr(self, a)
            r = repr(value)
            print(f'{prefix}{key} : {r}')
        print('+ ' + '- ' * block_size)
        return self

    def format_doc(self, default, type_: type, doc: str):
        res = '{: >5}, default: {}'.format(type_.__name__, repr(default))
        if doc:
            res += ' - ' + doc
        return res

    def _get_attrs(self):
        return [
            a for a in dir(self.__class__)
            if not a.startswith('_') and not callable(getattr(self, a))
        ]

    def _get_resolvers_map(self) -> Dict[str, Callable]:
        res = {}
        for attr in self._attrs:
            func_name = f'resolve_' + attr
            func = getattr(self, func_name, None)
            if func and callable(func):
                res[attr] = func
        return res

    def _setup_arguments(self):
        """
        Setup argument parser.
        """
        for attr in self._attrs:
            value = getattr(self, attr)
            if isinstance(value, (tuple, list)):
                self._manage_tuple(attr, value)
            else:
                self._call_definer(attr, value)

    def _parse_arguments(self, args=None):
        self._args = self._parser.parse_args(args)

    def _fill_attributes(self, obj=None):
        """
        Fill `obj` with defined attributes. If `obj` is `None` - fill `self`.
        This method should be called after arguments parsings.
        """
        if obj is None:
            obj = self
        for a in self._attrs:
            value = getattr(self._args, a)
            if a in self._resolvers:
                value = self._resolvers[a](value)
            setattr(obj, a, value)

    def _call_definer(self, attr: str, value, doc='', typ=None):
        typ = typ or type(value)
        definer = self._define_map.get(typ, None)
        if definer is None:
            print(value, typ, definer)
            raise ConfigurationError("Unknown type for field '{0}'. "
                                     "Should be primitive type.".format(attr))
        definer(attr, value, doc)

    def _define_str(self, attr, value, doc=''):
        # doc = 'String field, default={}. {}'.format(repr(value), doc).strip()
        self._define_arg(attr, str, value, doc)

    def _define_int(self, attr, value, doc=''):
        # doc = 'Integer field, default={}. {}'.format(repr(value), doc).strip()
        self._define_arg(attr, int, value, doc)

    def _define_float(self, attr, value, doc=''):
        # doc = 'Float field, default={}. {}'.format(repr(value), doc).strip()
        self._define_arg(attr, float, value, doc)

    def _attr_name_tuple(self, attr):
        """
        >>> self._attr_name_tuple('a')
        ('-a', '--a')

        >>> self._attr_name_tuple('aa')
        ('--a',)
        """
        if len(attr) > 1:
            return ('--' + attr,)
        else:
            return ('-' + attr, '--' + attr)

    def _define_bool(self, attr, value, doc=''):
        # doc = 'Boolean flag, default={}. {}'.format(repr(value), doc).strip()
        doc = self.format_doc(value, bool, doc)
        feature_parser = self._parser.add_mutually_exclusive_group(required=False)
        attr_name = self._attr_name_tuple(attr)
        feature_parser.add_argument(*attr_name, dest=attr, action='store_true', help=doc)
        attr_name = self._attr_name_tuple('no-' + attr)
        feature_parser.add_argument(*attr_name, dest=attr, action='store_false')
        self._parser.set_defaults(**{attr: value})

    def _manage_tuple(self, attr, value):
        err_msg = "Bad definition for field '{0}'. Tuple must have one of the next formats: " \
                  "(default_value, docstring) or (default_value, type, docstring)".format(attr)
        if len(value) == 2:
            value, doc = value
            typ = type(value)
        elif len(value) == 3:
            value, typ, doc = value
        else:
            raise ConfigurationError(err_msg)
        if type(typ) is not type or type(doc) is not str:
            raise ConfigurationError(err_msg)
        self._call_definer(attr, value, doc, typ)

    def _define_arg(self, attr: str, type_, value, doc='', action=None):
        doc = self.format_doc(value, type_, doc)
        params = {
            'dest': attr,
            'type': type_,
            'default': value,
            'help': doc,
            'action': action
        }
        if action and action.startswith('store'):
            params.pop('type')
        attr_name = self._attr_name_tuple(attr)
        self._parser.add_argument(*attr_name, **params)


# backward compatibility
BaseConfig = SimpleConfig


class Config(SimpleConfig):
    def _get_attrs(self):
        attrs = []
        for attr in dir(self):
            value = getattr(self, attr)
            if attr.startswith('_') or not isinstance(value, Field):
                continue
            attrs.append(attr)
        return attrs

    def _setup_arguments(self):
        """
        Setup argument parser.
        """
        for attr in self._attrs:
            field = getattr(self, attr)  # type: Field
            self._call_definer(attr, field.default, field.doc, field.type)

    def _get_resolvers_map(self) -> Dict[str, Callable]:
        res = {}
        for attr in self._attrs:
            field = getattr(self.__class__, attr)
            if isinstance(field, MethodField):
                field.method = field.method or 'resolve_' + attr
                func = getattr(self, field.method, None)
                if func:
                    res[attr] = func
        return res
