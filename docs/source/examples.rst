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
        from restae.serializers import ModelSerializer


        class User(ndb.Model):
            email = ndb.StringProperty()
            first_name = ndb.StringProperty()
            last_name = ndb.StringProperty()


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



This will generate the following routes

    .. code-block:: python

        GET     /user/                         \ list action
        GET     /user                          \ list action (idem without trailing slash)

        GET     /user/<user key urlsafe>/      \ retrieve action
        GET     /user/<user key urlsafe>       \ retrieve action (idem without trailing slash)

        POST    /user/                         \ create action
        POST    /user                          \ create action (idem without trailing slash)

        PUT     /user/<user key urlsafe>/      \ update action
        PUT     /user/<user key urlsafe>       \ update action (idem without trailing slash)

        PATCH   /user/<user key urlsafe>/      \ partial_update action
        PATCH   /user/<user key urlsafe>       \ partial_update action (idem without trailing slash)

        DELETE  /user/<user key urlsafe>/      \ destroy action
        DELETE  /user/<user key urlsafe>       \ destroy action (idem without trailing slash)