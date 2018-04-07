import argparse


class ConfigurationError(Exception):
    pass


class BaseConfig(object):
    _desc = None

    def __init__(self, desc=None, strict=False):
        self._attrs = [a for a in dir(self)
                       if not a.startswith('_')
                       and not callable(getattr(self, a))]
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
            return
        for attr in self._attrs:
            value = getattr(self, attr)
            typ = type(value)
            if typ is tuple or typ is list:
                self._manage_tuple(attr, value)
            else:
                self._call_definer(attr, typ, value)

        self._args = self._parser.parse_args()
        self.fill_attributes(self)
        self._defined = True

    def fill_attributes(self, obj):
        """
        Fill `obj` with defined attributes.
        """
        if not self._defined:
            self.define()
        for a in self._attrs:
            setattr(obj, a, getattr(self._args, a))

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
            print(f'{prefix}{key} : {value}')
        print('+ ' + '- ' * block_size)

    def _call_definer(self, attr: str, typ, value, doc=''):
        definer = self._define_map.get(typ, None)
        if definer is None:
            raise ConfigurationError("Unknown type for field '{0}'. "
                                     "Should be primitive type.".format(attr))
        definer(attr, value, doc)

    def _define_str(self, attr, value, doc=None):
        doc = doc or 'string field'
        self._define_arg(attr, str, value, doc)

    def _define_int(self, attr, value, doc=None):
        doc = doc or 'int field'
        self._define_arg(attr, int, value, doc)

    def _define_float(self, attr, value, doc=None):
        doc = doc or 'float field'
        self._define_arg(attr, float, value, doc)

    def _define_bool(self, attr, value, doc=None):
        doc = doc or 'boolean flag'
        action = 'store_false' if value else 'store_true'
        self._define_arg(attr, str, value, doc, action=action)

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
        dash = '-' * min(2, len(attr))
        self._parser.add_argument(dash + attr, **params)


class ExampleConfig(BaseConfig):
    _desc = 'Description for parser. Will be redefined if `desc` is specified for config object.'
    a = 3
    b = False
    h = True
    c = 'spam', 'field with value and doc string'  # type: str
    ddd = None, int, 'field with value, type and doc string'  # type: int


def main():
    conf = ExampleConfig(desc='Example config')
    conf.define()
    conf.print()


if __name__ == '__main__':
    main()
