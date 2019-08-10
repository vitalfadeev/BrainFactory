from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from . import views


urlpatterns = [
    path("my",                  views.my,       name="my"),
    path("send",                views.send,     name="send"),
    path("send1",               views.send1,    name="send1"),
    path('send2/<int:batch_id>',views.send2,    name='send2'),
    path('send3/<int:batch_id>',views.send3,    name='send3'),
    path('view/<int:batch_id>', views.view,     name='view'),
    path("public",              views.public,   name="public"),
    path("",                    views.home,     name="home"),
]
