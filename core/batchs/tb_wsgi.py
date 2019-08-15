def tb_wsgi_app(environ, start_response, batch_id):
    from tensorboard import default
    from tensorboard import program
    from tensorboard.backend import application
    from django import conf

    # fix. ungzip
    # request.headers unset 'Accept-Encoding'
    #   ? 'HTTP_ACCEPT_ENCODING'
    # then set again

    #program.main(default.get_plugins(), default.get_assets_zip_provider())
    plugins = default.get_plugins()
    #assets_zip_provider = program.get_default_assets_zip_provider()
    assets_zip_provider = None
    #server_class =

    #tb_wsgi = program.create_tb_app(plugins, assets_zip_provider)
    tensorboard = program.TensorBoard(plugins, assets_zip_provider)


    argv = [__file__,
        '--logdir={}/tf-logs/{}'.format(conf.settings.BASE_DIR, batch_id),
        '--path_prefix=/view/{}'.format(batch_id)
    ]
    tensorboard.configure(argv=argv)

    app = application.standard_tensorboard_wsgi(tensorboard.flags,
                                                tensorboard.plugin_loaders,
                                                tensorboard.assets_zip_provider)


    #tensorboard.flags.logdir = "tf-logs/{}".format(batch_id)
    #tensorboard.flags.path_prefix = "/view/{}".format(batch_id)

    #tb_wsgi.data_applications[clean_path](environ, start_response)  # wrapped @wrappers.Request.application
    #for k in tb_wsgi.data_applications.keys():
    #    print(k)

    #for a,b in environ.items():
    #    print(a, "\t", b)

    # set again request.headers: 'Accept-Encoding'

    return app(environ, start_response)
    #return tb_wsgi(environ, start_response)

