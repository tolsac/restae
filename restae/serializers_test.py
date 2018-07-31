"""
Serializers test
"""
import unittest
import sys
import datetime

import dev_appserver
sys.path = dev_appserver.EXTRA_PATHS + sys.path

from google.appengine.ext import testbed, ndb

from restae import serializers


class UserModel(ndb.Model):
    email = ndb.StringProperty()
    last_name = ndb.StringProperty()
    first_name = ndb.StringProperty()
    age = ndb.IntegerProperty()


class UserSerializer(serializers.Serializer):
    email = serializers.StringField()
    first_name = serializers.StringField()
    last_name = serializers.StringField()
    age = serializers.IntegerField()


class UserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = '__all__'


class AllFields(ndb.Model):
    float_val = ndb.FloatProperty()
    int_val = ndb.IntegerProperty()
    datetime_val = ndb.DateTimeProperty()
    bool_val = ndb.BooleanProperty()
    string_val = ndb.StringProperty()
    text_val = ndb.TextProperty()
    user_val = ndb.KeyProperty()


class AllFieldsSerializer(serializers.Serializer):
    float_val = serializers.FloatField()
    int_val = serializers.IntegerField()
    datetime_val = serializers.DatetimeField()
    bool_val = serializers.BooleanField()
    string_val = serializers.StringField()
    text_val = serializers.StringField()
    user_val = serializers.KeyField()


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        ndb.get_context().clear_cache()


class SerializerTestCase(BaseTestCase):

    def test_serializer_output(self):
        entity = UserModel(
            email='admin@restae.com',
            first_name='admin',
            last_name='restae',
            age=28
        )
        entity.put()
        serialized = UserSerializer(entity).data
        self.assertDictEqual(
            serialized,
            {
                'key': entity.key.urlsafe(),
                'email': u'admin@restae.com',
                'first_name': u'admin',
                'last_name': u'restae',
                'age': 28
            }
        )

    def test_serializer_input(self):
        api_data = {
            'email': 'admin@restae.com',
            'first_name': 'admin',
            'last_name': 'restae',
            'age': 28
        }

        serialized = UserSerializer(data=api_data).data
        self.assertDictEqual(
            serialized,
            {
                'email': u'admin@restae.com',
                'first_name': u'admin',
                'last_name': u'restae',
                'age': 28
            }
        )

    def test_all_fields_output(self):
        user = UserModel(email='admin@restae.com')
        user.put()

        all_fields = AllFields(
            float_val=3.14,
            int_val=42,
            datetime_val=datetime.datetime(2018, 1, 1),
            bool_val=True,
            string_val='restae',
            text_val='framework',
            user_val=user.key
        )
        all_fields.put()

        self.assertDictEqual(
            AllFieldsSerializer(all_fields).data,
            {
                'key': all_fields.key.urlsafe(),
                'float_val': 3.14,
                'int_val': 42,
                'datetime_val': '2018-01-01T00:00:00',
                'bool_val': True,
                'string_val': u'restae',
                'text_val': u'framework',
                'user_val': user.key.urlsafe()
            }
        )

    def test_all_fields_input(self):
        user = UserModel(email='admin@restae.com')
        user.put()

        api_data = {
            'float_val': 3.14,
            'int_val': 42,
            'datetime_val': '2018-01-01T00:00:00',
            'bool_val': True,
            'string_val': 'restae',
            'text_val': 'framework',
            'user_val': user.key.urlsafe()
        }

        serialized = AllFieldsSerializer(data=api_data).data
        key_obj = serialized.pop('user_val')

        self.assertEqual(
            key_obj.__class__,
            ndb.Key
        )
        self.assertEqual(
            key_obj.kind(),
            'UserModel'
        )

        self.assertDictEqual(
            serialized,
            {
                'float_val': 3.14,
                'int_val': 42,
                'datetime_val': datetime.datetime(2018, 1, 1, 0, 0),
                'bool_val': True,
                'string_val': 'restae',
                'text_val': 'framework',
            }
        )

    def test_source_attr(self):
        user = UserModel(email='admin@restae.com')
        user.put()

        class UserSerializer(serializers.Serializer):
            contact = serializers.StringField(source='email')

        serialized = UserSerializer(user).data
        self.assertDictEqual(
            serialized,
            {
                'key': user.key.urlsafe(),
                'contact': 'admin@restae.com'
            }
        )


class ModelSerializerTestCase(BaseTestCase):
    def test_model_serializer_output(self):
        entity = UserModel(
            email='admin@restae.com',
            first_name='admin',
            last_name='restae',
            age=28
        )
        entity.put()
        serialized = UserModelSerializer(entity).data

        self.assertDictEqual(
            serialized,
            {
                'key': entity.key.urlsafe(),
                'email': u'admin@restae.com',
                'first_name': u'admin',
                'last_name': u'restae',
                'age': 28
            }
        )

    def test_model_serializer_with_filter_output(self):
        entity = UserModel(
            email='admin@restae.com',
            first_name='admin',
            last_name='restae',
            age=28
        )
        entity.put()
        UserModelSerializer.Meta.fields = ('key', 'email')
        serialized = UserModelSerializer(entity).data

        self.assertDictEqual(
            serialized,
            {
                'key': entity.key.urlsafe(),
                'email': u'admin@restae.com'
            }
        )


if __name__ == '__main__':
    unittest.main()
