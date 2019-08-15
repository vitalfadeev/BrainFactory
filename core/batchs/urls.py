from django.urls import path, re_path
from django.contrib.auth.decorators import login_required
from core.batchs.tb_wsgi import tb_wsgi_app
from . import wsgi_view
from . import views


urlpatterns = [
    # My
    path("my",                          views.my,                                   name="my"),
    path("my/ajax",                     login_required(views.MyAjax.as_view()),     name="my/ajax"),
    # Send
    path("send",                        views.send,                                 name="send"),
    path("send1",                       views.send1,                                name="send1"),
    path('send2/<int:batch_id>',        views.send2,                                name='send2'),
    path('send2/<int:batch_id>/ajax',   login_required(views.Send2Ajax.as_view()),  name="send2/id/ajax"),
    path('send3/<int:batch_id>',        views.send3,                                name='send3'),
    # View
    path('view/<int:batch_id>',         views.view,                                 name='view'),
    # TensorBoard
    path('view/<int:batch_id>/tb',      views.tb,                                   name='rb'),
    re_path(r"view/(?P<batch_id>\d+)/data/",  wsgi_view.WsgiView.as_view(application=tb_wsgi_app), name='view_id_tb'), #  JSON
    # Public
    path("public",                      views.public,                               name="public"),
    path('public/ajax',                 views.PublicAjax.as_view(),                 name="public/ajax"),
    path("",                            views.home,                                 name="home"),
]
