"""
Serializers
"""
import datetime
import collections

from dateutil import parser

from exceptions import ValidationError, SerializerError
from helpers import get_key_from_urlsafe, KEY_CLASS


def get_attribute(obj, name):
    if issubclass(obj.__class__, collections.Mapping):
        if name in obj:
            return obj[name]
    attr = getattr(obj, name, None)

    if attr is None:
        raise SerializerError('Missing attribute {} on {}'.format(
            name, obj
        ))
    return attr


def has_attribute(obj, name):
    if issubclass(obj.__class__, collections.Mapping):
        if name in obj:
            return True
    attr = getattr(obj, name, None)

    if attr is None:
        return False
    return True


class Field(object):
    base_type = None

    def __init__(self, *args, **kwargs):
        self.is_many = kwargs.get('many', False)
        self.object = None if len(args) == 0 else args[0]
        self._data = kwargs.get('data', None)
        self.args = args
        self.kwargs = kwargs

        self.required = kwargs.get('required', False)
        self.source = kwargs.get('source', None)

    def input(self, value):
        if self.base_type is not None:
            try:
                return self.base_type(value)
            except Exception:
                raise ValidationError('Field: Unknown {} value: {}'.format(
                    self.__class__.__name__, value))
        return value

    def input_many(self, values):
        if self.is_many:
            return [
                self.input(value)
                for value in values
            ]
        else:
            return self.input(values)

    def output(self, value):
        return value

    def output_many(self, values):
        if self.is_many:
            return [
                self.output(value)
                for value in values
            ]
        else:
            return self.output(values)

    def validate_base_type(self, value):
        if self.base_type is not None:
            return isinstance(value, self.base_type)
        return True

    def serialize(self):
        """
        ---> si y'a un data={} on veux verifier que les fields sont bien types, pas de manquant etc..
        ---> si pas de data, on a un objet et on veux le mettre en dict
        """
        if self._data is None and self.object is not None:
            return self.output_many(self.object)
        elif self.object is None and self._data is not None:
            return self.input_many(self._data)
        else:
            raise SerializerError('If no positional argument are passed, you must use data= kwarg')

    @property
    def data(self):
        if self.is_many:
            return [
                self.__class__(obj, data=self._data).serialize()
                for obj in self.object
            ]
        return self.serialize()


class BooleanField(Field):
    base_type = bool
    TRUE_VALUES = [
        't', 'T',
        'y', 'Y', 'yes', 'YES',
        'true', 'True', 'TRUE',
        'on', 'On', 'ON',
        '1', 1,
        True
    ]
    FALSE_VALUES = [
        'f', 'F',
        'n', 'N', 'no', 'NO',
        'false', 'False', 'FALSE',
        'off', 'Off', 'OFF',
        '0', 0, 0.0,
        False
    ]

    def input(self, value):
        if value in self.TRUE_VALUES:
            return True
        elif value in self.FALSE_VALUES:
            return False
        raise ValidationError('Field: Unknown Boolean value: {}'.format(value))


class IntegerField(Field):
    base_type = int


class StringField(Field):
    base_type = str


class FloatField(Field):
    base_type = float


class KeyField(Field):
    base_type = KEY_CLASS

    def input(self, value):
        try:
            return get_key_from_urlsafe(value)
        except Exception:
            raise ValidationError('Field: Unknown Key value: {}'.format(value))

    def output(self, value):
        if not self.validate_base_type(value):
            raise ValidationError('Field: Needs a Key class, {} given'.format(value.__class__.__name__))
        return value.urlsafe()


class DatetimeField(Field):
    base_type = datetime.datetime

    def input(self, value):
        try:
            if 'format' in self.kwargs:
                return datetime.datetime.strptime(value, self.kwargs['format'])
            return parser.parse(value)
        except Exception:
            raise ValidationError('Field: Unknown {} value: {}'.format(
                self.__class__.__name__, value))

    def output(self, value):
        if 'format' in self.kwargs:
            return value.strftime(value, self.kwargs['format'])
        return value.isoformat()


TYPE_MAPPING = {
    'IntegerProperty': IntegerField,
    'FloatProperty': FloatField,
    'BooleanProperty': BooleanField,
    'StringProperty': StringField,
    'TextProperty': StringField,
    'DateTimeProperty': DatetimeField,
    'KeyProperty': KeyField
}


class Serializer(Field):
    def get_class_fields(self):
        _attrs = {}

        for key, value in self.__class__.__dict__.iteritems():
            if issubclass(value.__class__, Field):
                _attrs[key] = value
        return _attrs

    def input(self, data):
        payload = {}

        for attr, field in self.get_class_fields().iteritems():
            _source = field.source or attr
            if not has_attribute(data, _source) and field.required:
                raise SerializerError('{} requires field {} but is missing'.format(
                    self.__class__.__name__,
                    attr
                ))

            if has_attribute(data, _source):
                payload.update({
                    attr: field.input_many(get_attribute(data, _source))
                })

        return payload

    def output(self, obj):
        payload = {}

        for attr, field in self.get_class_fields().iteritems():
            _source = field.source or attr
            payload.update({
                attr: field.output_many(getattr(obj, _source))
            })
        payload['key'] = obj.key.urlsafe()
        return payload


class ModelSerializer(Serializer):
    def get_class_fields(self):
        _attrs = {}

        _meta = getattr(self, 'Meta', None)
        if _meta.fields == '__all__':
            _fields = _meta.model._properties.keys()
        else:
            _fields = _meta.fields

        for field in _fields:
            if field == 'key':
                _attrs[field] = KeyField()
            else:
                try:
                    _attrs[field] = TYPE_MAPPING[_meta.model._properties[field].__class__.__name__]()
                except KeyError:
                    raise SerializerError('Field {} doest not exists on {} or its type is not supported yet'.format(
                        field, _meta.model.__class__.__name__
                    ))
        return _attrs

