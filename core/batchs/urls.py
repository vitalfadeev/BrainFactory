from django.urls import path, re_path
from django.contrib.auth.decorators import login_required
from core.batchs.tb_wsgi import tb_wsgi_app
from . import wsgi_view
from . import views


urlpatterns = [
    # My
    path("my",                              views.my,                                   name="my"),
    path("my/ajax",                         login_required(views.my_ajax.as_view()),    name="my/ajax"),        # JSON

    # Send
    path("send",                            views.send,                                 name="send"),
    path("send1",                           views.send1,                                name="send1"),
    path('send2/<int:batch_id>',            views.send2,                                name='send2'),
    path('send2/<int:batch_id>/ajax',       login_required(views.send2_id_ajax.as_view()),
                                                                                        name="send2/id/ajax"),  # JSON
    path('send3/<int:batch_id>',            views.send3,                                name='send3'),

    # View
    path('view/<int:batch_id>',             views.view,                                 name='view'),
    path('view/<int:batch_id>/tensorboard', views.view,                                 name='view_tensorboard'),
    path('view/<int:batch_id>/tensorboard-self',
                                            views.view_tb_static,                       name='view_tensorboard_self'),
    path('view/<int:batch_id>/tb',          views.view_tb,                              name='view_tb'),
    re_path(r'(?P<prefix>font-roboto)/(?P<tail>.*)$',
                                            views.redirect_view),
    re_path(r'view/(?P<batch_id>\d+)/(?P<prefix>tf-interactive-inference-dashboard)/(?P<tail>.*)$',
                                            views.redirect_view),
    path('view/<int:batch_id>/solved/ajax',
                                            login_required(views.view_id_solved_ajax.as_view()),
                                                                                        name="view/id/solved/ajax"),  # JSON
    re_path(r"view/(?P<batch_id>\d+)/data/",
                                            wsgi_view.WsgiView.as_view(application=tb_wsgi_app),
                                                                                        name='view_id_tb'),     # JSON
    path('view/<int:batch_id>/export/input/csv',
                                            views.view_export_input_csv,                name='view_export_input_csv'),
    path('view/<int:batch_id>/export/solved/csv',
                                            views.view_export_solved_csv,               name='view_export_solved_csv'),
    path('view/<int:batch_id>/export/input/xls',
                                            views.view_export_input_xls,                name='view_export_input_xls'),
    path('view/<int:batch_id>/export/solved/xls',
                                            views.view_export_solved_xls,               name='view_export_solved_xls'),
    path('view/<int:batch_id>/graph',
                                            views.view_graph,                           name='view_id_graph'),
    path('graph',                           views.graph,                                name='graph'),
    # Public
    path("public",                          views.public,                               name="public"),
    path('public/ajax',                     views.PublicAjax.as_view(),                 name="public/ajax"),    # JSON
    path("",                                views.home,                                 name="home"),
]
