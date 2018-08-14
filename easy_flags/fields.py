from typing import Callable, List, Optional, Union

from easy_flags.errors import ValidationError


Allowed = Union[int, float, str, bool, None]
Validators = Optional[List[Callable]]


class Field(object):
    def __init__(self, default: Allowed = None, doc='',
                 validators: Validators = None,
                 type_: Optional[type] = None):
        self.default = default
        self.value = default
        self.doc = doc
        self.type = type_ or type(default)
        self.validators = validators or []

    def validate(self):
        errors = []
        for validator in self.validators:
            try:
                ok = validator(self.value)
                if ok is False:
                    errors.append(self._format_error(validator))
            except ValidationError as e:
                errors.append(self._format_error(validator, e))
        return errors

    def _format_error(self, validator, error=None):
        res = validator.__name__
        if error:
            res += ': ' + str(error)
        return res


class BoolField(Field):
    def __init__(self, default: Optional[bool] = None, doc='',
                 validators: Validators = None):
        super().__init__(default, doc, validators)
        self.type = bool


class FloatField(Field):
    def __init__(self, default: Optional[float] = None, doc='',
                 validators: Validators = None):
        super().__init__(default, doc, validators)
        self.type = float


class IntField(Field):
    def __init__(self, default: Optional[int] = None, doc='',
                 validators: Validators = None):
        super().__init__(default, doc, validators)
        self.type = int


class StringField(Field):
    def __init__(self, default: Optional[str] = None, doc='',
                 validators: Validators = None):
        super().__init__(default, doc, validators)
        self.type = str


class MethodField(Field):
    def __init__(self, field: Field, method: Optional[str] = None):
        super().__init__(field.default, field.doc)
        self.type = field.type
        self.method = method
