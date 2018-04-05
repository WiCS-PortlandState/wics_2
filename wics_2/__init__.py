from pyramid.config import Configurator


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('hackathon-home', '/hackathon')
    config.add_route('hackathon-schedule', '/hackathon/schedule')
    config.add_route('hackathon-register', '/hackathon/register')
    config.add_route('hackathon-contact', '/hackathon/contact')
    config.add_route('githubdeploy', '/githubdeploy')
    config.scan()
    return config.make_wsgi_app()
