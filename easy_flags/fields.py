from typing import Optional, Union


Allowed = Union[int, float, str, bool, None]


class Field(object):
    def __init__(self, default: Allowed = None, doc='',
                 type_: Optional[type] = None):
        self.default = default
        self.doc = doc
        self.type = type_ or type(default)


class BoolField(Field):
    def __init__(self, default: Optional[bool] = None, doc=''):
        super().__init__(default, doc)
        self.type = bool


class FloatField(Field):
    def __init__(self, default: Optional[float] = None, doc=''):
        super().__init__(default, doc)
        self.type = float


class IntField(Field):
    def __init__(self, default: Optional[int] = None, doc=''):
        super().__init__(default, doc)
        self.type = int


class StringField(Field):
    def __init__(self, default: Optional[str] = None, doc=''):
        super().__init__(default, doc)
        self.type = str


class MethodField(Field):
    def __init__(self, field: Field, method: Optional[str] = None):
        super().__init__(field.default, field.doc)
        self.type = field.type
        self.method = method
