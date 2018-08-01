Examples
============

Let's take a look at a quick example of using restae to build a simple model-backed API.
We'll create a read-write API for accessing information on the users of our project.
Any global settings for the API are kept in a single configuration dictionary named RESTAE_SETTINGS.


    .. code-block:: python

        import webapp2

        from google.appengine.ext import ndb

        from restae.handlers import APIModelHandler
        from restae.router import Router
        from restae.serializers import Serializer, ModelSerializer, StringField, KeyField


        class User(ndb.Model):
            email = ndb.StringProperty()
            first_name = ndb.StringProperty()
            last_name = ndb.StringProperty()


        class UserSerializer(Serializer):
            key = KeyField()
            email = StringField()


        class UserModelSerializer(ModelSerializer):
            class Meta:
                model = User
                fields = '__all__'


        class Handler(APIModelHandler):
            queryset = User.query()
            serializer_class = UserModelSerializer


        router = Router()
        router.register('user', Handler)

        app = webapp2.WSGIApplication(router.urls)
