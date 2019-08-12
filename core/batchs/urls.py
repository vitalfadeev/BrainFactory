from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required
from . import views


urlpatterns = [
    path("my",                          views.my,                                   name="my"),
    path("my_ajax",                     login_required(views.MyAjax.as_view()),     name="my_ajax"),
    path("send",                        views.send,                                 name="send"),
    path("send1",                       views.send1,                                name="send1"),
    path('send2/<int:batch_id>',        views.send2,                                name='send2'),
    path('send2_ajax/<int:batch_id>',   login_required(views.Send2Ajax.as_view()),  name="send2_ajax"),
    path('send3/<int:batch_id>',        views.send3,                                name='send3'),
    path('view/<int:batch_id>',         views.view,                                 name='view'),
    path("public",                      views.public,                               name="public"),
    path('public_ajax',                 views.PublicAjax.as_view(),                 name="public_ajax"),
    path("",                            views.home,                                 name="home"),
]
