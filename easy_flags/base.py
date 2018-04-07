import argparse


class ConfigurationError(Exception):
    pass


class BaseConfig(object):
    _desc = None

    def __init__(self, desc=None, strict=False):
        self.attrs = [a for a in dir(self)
                      if not a.startswith('_')
                      and not callable(getattr(self, a))]
        self.define_map = {
            str: self.define_str,
            int: self.define_int,
            float: self.define_float,
            bool: self.define_bool,
        }
        conflict_handler = 'error' if strict else 'resolve'
        self.parser = argparse.ArgumentParser(description=desc or self._desc,
                                              conflict_handler=conflict_handler)
        self.args = None
        self.defined = False

    def call_definer(self, attr: str, typ, value, doc=''):
        definer = self.define_map.get(typ, None)
        if definer is None:
            raise ConfigurationError("Unknown type for field '{0}'. "
                                     "Should be primitive type.".format(attr))
        definer(attr, value, doc)

    def define_str(self, attr, value, doc=None):
        doc = doc or 'string value'
        self.define_arg(attr, str, value, doc)

    def define_int(self, attr, value, doc=None):
        doc = doc or 'int value'
        self.define_arg(attr, int, value, doc)

    def define_float(self, attr, value, doc=None):
        doc = doc or 'float value'
        self.define_arg(attr, float, value, doc)

    def define_bool(self, attr, value, doc=None):
        doc = doc or 'boolean flag'
        action = 'store_false' if value else 'store_true'
        self.define_arg(attr, str, value, doc, action=action)

    def manage_tuple(self, attr, value):
        if len(value) == 2:
            value, doc = value
            typ = type(value)
        elif len(value) == 3:
            value, typ, doc = value
        else:
            raise ConfigurationError("Improper configuration for field '{0}'. Config field should be "
                                     "primitive or tuple with length 2 or 3.".format(attr))
        self.call_definer(attr, typ, value, doc)

    def define_arg(self, attr: str, typ, value, doc='', action=None):
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
        self.parser.add_argument(dash + attr, **params)

    def define(self):
        if self.defined:
            return
        for attr in self.attrs:
            value = getattr(self, attr)
            typ = type(value)
            if typ is tuple or typ is list:
                self.manage_tuple(attr, value)
            else:
                self.call_definer(attr, typ, value)

        self.args = self.parser.parse_args()
        self.fill_attributes(self)
        self.defined = True

    def fill_attributes(self, obj):
        for a in self.attrs:
            setattr(obj, a, getattr(self.args, a))

    def print(self, title=None, block_size=39, prefix='|  '):
        if not self.defined:
            self.define()
        max_len = max([len(a) for a in self.attrs])
        print('+ ' + '- ' * block_size)
        if title:
            print(prefix + title)
        for a in self.attrs:
            key = a.ljust(max_len)
            value = getattr(self, a)
            print(f'{prefix}{key} : {value}')
        print('+ ' + '- ' * block_size)


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
