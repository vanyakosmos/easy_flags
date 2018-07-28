import argparse
from typing import Optional


# will point to the latest defined config
CONFIG = None  # type: Optional[BaseConfig]


class ConfigurationError(Exception):
    pass


class BaseConfig(object):
    _desc = None

    def __init__(self, desc=None, strict=False):
        self._attrs = [a for a in dir(self)
                       if not a.startswith('_')
                       and not callable(getattr(self, a))]
        self._resolvers = self._get_resolvers_map()
        self._define_map = {
            str: self._define_str,
            int: self._define_int,
            float: self._define_float,
            bool: self._define_bool,
        }
        conflict_handler = 'error' if strict else 'resolve'
        self._parser = argparse.ArgumentParser(description=desc or self._desc,
                                               conflict_handler=conflict_handler)
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
        self.fill_attributes()
        globals()['CONFIG'] = self
        return self

    def fill_attributes(self, obj=None):
        """
        Fill `obj` with defined attributes.
        """
        if obj is None:
            obj = self
        if not self._defined:
            self.define()
        for a in self._attrs:
            value = getattr(self._args, a)
            if a in self._resolvers:
                value = self._resolvers[a](value)
            setattr(obj, a, value)

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

    def _setup_arguments(self):
        for attr in self._attrs:
            value = getattr(self, attr)
            typ = type(value)
            if typ is tuple or typ is list:
                self._manage_tuple(attr, value)
            else:
                self._call_definer(attr, typ, value)

    def _parse_arguments(self, args=None):
        self._args = self._parser.parse_args(args)
        # check `defined` flag before fill() in order to escape recursion calls
        self._defined = True

    def _get_resolvers_map(self):
        attrs_set = set(self._attrs)
        resolve_prefix = 'resolve_'
        resolve_cut = len(resolve_prefix)
        return {
            a[resolve_cut:]: getattr(self, a)
            for a in dir(self)
            if (
                a.startswith('resolve_') and
                a[resolve_cut:] in attrs_set and
                callable(getattr(self, a))
            )
        }

    def _call_definer(self, attr: str, typ, value, doc=''):
        definer = self._define_map.get(typ, None)
        if definer is None:
            raise ConfigurationError("Unknown type for field '{0}'. "
                                     "Should be primitive type.".format(attr))
        definer(attr, value, doc)

    def _define_str(self, attr, value, doc=''):
        doc = 'String field, default={}. {}'.format(repr(value), doc).strip()
        self._define_arg(attr, str, value, doc)

    def _define_int(self, attr, value, doc=''):
        doc = 'Integer field, default={}. {}'.format(repr(value), doc).strip()
        self._define_arg(attr, int, value, doc)

    def _define_float(self, attr, value, doc=''):
        doc = 'Float field, default={}. {}'.format(repr(value), doc).strip()
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
        doc = 'Boolean flag, default={}. {}'.format(repr(value), doc).strip()
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
        self._call_definer(attr, typ, value, doc)

    def _define_arg(self, attr: str, typ, value, doc='', action=None):
        params = {
            'dest': attr,
            'type': typ,
            'default': value,
            'help': doc,
            'action': action
        }
        if action and action.startswith('store'):
            params.pop('type')
        attr_name = self._attr_name_tuple(attr)
        self._parser.add_argument(*attr_name, **params)


class ExampleConfig(BaseConfig):
    _desc = 'Description for parser. Will be redefined if `desc` is specified for config object.'
    # specify type of resolver
    a = 3  # type: str
    cache = True
    d = False
    g = 5
    c = 'spam', 'field with value and doc string'  # type: str
    ddd = None, int, 'field with value, type and doc string'  # type: int

    def resolve_a(self, value):
        return str(value * 42)


def main():
    conf = ExampleConfig(desc='Example config').define().print()
    print(conf is CONFIG)


if __name__ == '__main__':
    main()
