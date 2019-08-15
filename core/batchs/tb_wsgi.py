def tb_wsgi_app(environ, start_response, batch_id):
    from tensorboard import default
    from tensorboard import program

    # fix. ungzip
    # request.headers unset 'Accept-Encoding'
    #   ? 'HTTP_ACCEPT_ENCODING'
    # then set again

    #program.main(default.get_plugins(), default.get_assets_zip_provider())
    plugins = default.get_plugins()
    #assets_zip_provider = default.get_assets_zip_provider()
    assets_zip_provider = None
    program.FLAGS.logdir = "tf-logs/{}".format(batch_id)
    program.FLAGS.path_prefix = "/view/{}".format(batch_id)

    tb_wsgi = program.create_tb_app(plugins, assets_zip_provider)

    #tb_wsgi.data_applications[clean_path](environ, start_response)  # wrapped @wrappers.Request.application
    #for k in tb_wsgi.data_applications.keys():
    #    print(k)

    #for a,b in environ.items():
    #    print(a, "\t", b)

    # set again request.headers: 'Accept-Encoding'

    return tb_wsgi(environ, start_response)

