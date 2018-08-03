# restae
[![Build Status](https://travis-ci.org/tolsac/restae.svg?branch=master)](https://travis-ci.org/tolsac/restae) 
[![PyPI version](https://badge.fury.io/py/restae.svg)](https://badge.fury.io/py/restae)

Restae is a framework to build REST APIs within the Google Cloud Platform App Engine. The structure of the framework is highly inspired by Django and Django REST Framework.

Please checkout official documentation to get more information https://restae.readthedocs.io/en/latest/



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

Will produces those endpoints

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