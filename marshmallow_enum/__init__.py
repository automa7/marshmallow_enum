from enum import Enum
from marshmallow import ValidationError
from marshmallow.fields import Field

try:
    # ugh Python 2
    str_types = (str, unicode)  # noqa: F821
except:
    str_types = (str, )


class LoadDumpOptions(Enum):
    value = 1
    name = 0


class EnumField(Field):
    VALUE = LoadDumpOptions.value
    NAME = LoadDumpOptions.name

    default_error_messages = {
        'by_name': 'Invalid enum member {input}',
        'by_value': 'Invalid enum value {input}',
        'must_be_string': 'Enum name must be string'
    }

    def __init__(
            self, enum, by_value=False, load_by=None, dump_by=None, error='', *args, **kwargs
    ):
        self.enum = enum
        self.by_value = by_value
        self.error = error

        if load_by is None:
            load_by = LoadDumpOptions.value if by_value else LoadDumpOptions.name

        if load_by not in LoadDumpOptions:
            raise ValueError(
                'Invalid selection for load_by must be EnumField.VALUE or EnumField.NAME, got {}'.
                format(load_by)
            )

        if dump_by is None:
            dump_by = LoadDumpOptions.value if by_value else LoadDumpOptions.name

        if dump_by not in LoadDumpOptions:
            raise ValueError(
                'Invalid selection for load_by must be EnumField.VALUE or EnumField.NAME, got {}'.
                format(dump_by)
            )

        self.load_by = load_by
        self.dump_by = dump_by

        super(EnumField, self).__init__(*args, **kwargs)

    def _serialize(self, value, attr, obj):
        if value is None:
            return None
        elif self.dump_by == LoadDumpOptions.value:
            return value.value
        else:
            return value.name

    def _deserialize(self, value, attr, data):
        if value is None:
            return None
        elif self.load_by == LoadDumpOptions.value:
            return self._deserialize_by_value(value, attr, data)
        else:
            return self._deserialize_by_name(value, attr, data)

    def _deserialize_by_value(self, value, attr, data):
        try:
            return self.enum(value)
        except ValueError:
            self.fail('by_value', input=value)

    def _deserialize_by_name(self, value, attr, data):
        if not isinstance(value, str_types):
            self.fail('must_be_string', input=value)

        try:
            return getattr(self.enum, value)
        except AttributeError:
            self.fail('by_name', input=value)

    def fail(self, key, **kwargs):
        # depercation of name/value fail inputs
        if 'name' in kwargs:
            kwargs['input'] = kwargs['name']
        elif 'value' in kwargs:
            kwargs['input'] = kwargs['value']

        if self.error:
            if self.by_value:
                kwargs['choices'] = ', '.join([str(mem.value) for mem in self.enum])
            else:
                kwargs['choices'] = ', '.join([mem.name for mem in self.enum])
            msg = self.error.format(**kwargs)
            raise ValidationError(msg)
        else:
            super(EnumField, self).fail(key, **kwargs)
