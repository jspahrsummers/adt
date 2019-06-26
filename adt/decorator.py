from copy import copy
from enum import Enum
from typing import no_type_check


@no_type_check
def adt(cls):
    cls._Key = Enum(
        '_Key',
        [k for k in cls.__annotations__.keys() if not k.startswith('__')])

    def _init(self, key, value, orig_init=cls.__init__):
        self._key = key
        self._value = value
        orig_init(self)

    cls.__init__ = _init

    def _repr(self):
        return f'{type(self)}.{self._key}({self._value})'

    cls.__repr__ = _repr

    def _str(self):
        return f'<{type(self)}.{self._key}: {self._value}>'

    cls.__str__ = _str

    def _eq(self, other, cls=cls):
        if not isinstance(other, cls):
            return False

        return self._key == other._key and self._value == other._value

    cls.__eq__ = _eq

    for caseName, key in cls._Key.__members__.items():

        def constructor(cls, value, _key=key):
            return cls(key=_key, value=value)

        setattr(cls, caseName, classmethod(constructor))

        def accessor(self, _key=key):
            if self._key == _key:
                return self._value
            else:
                return None

        setattr(cls, caseName.lower(), property(fget=accessor))

    def match(self, **kwargs):
        cases = set(type(self)._Key.__members__.keys())
        predicates = {k.upper() for k in kwargs.keys()}

        assert cases == predicates, f'Pattern match on {self} ({predicates}) is over- or under-specified vs. {cases}'

        for key, callback in kwargs.items():
            if self._key == type(self)._Key[key.upper()]:
                return callback(self._value)

        raise ValueError(
            f'{self} failed pattern match against all of: {predicates}')

    cls.match = match

    return cls