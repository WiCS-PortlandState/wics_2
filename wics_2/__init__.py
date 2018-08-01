from pyramid.config import Configurator
from pyramid_beaker import session_factory_from_settings


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')
    config.include('pyramid_beaker')
    config.include('pyramid_tm')
    config.include('pyramid_retry')
    config.include('pyramid_scss')
    config.include('.models')

    # Session stuff
    session_factory = session_factory_from_settings(settings)
    config.set_session_factory(session_factory)

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('css', '/css/{css_path:.*}.css')
    config.add_view(route_name='css', view='pyramid_scss.controller.get_scss', renderer='scss', request_method='GET')
    config.add_route('home', '/')

    config.add_route('designer-home', '/design')

    # config.add_route('hackathon-home', '/hackathon')
    # config.add_route('hackathon-schedule', '/hackathon/schedule')
    # config.add_route('hackathon-register', '/hackathon/register')
    # config.add_route('hackathon-contact', '/hackathon/contact')
    # config.add_route('hackathon-sponsors', '/hackathon/sponsors')

    config.add_route('login', '/user/login')
    config.add_route('create-user', '/user/create')
    config.add_route('logout', '/user/logout')
    config.add_route('validate-username', '/user/validate-username')
    config.add_route('user-home', '/user/')
    config.add_route('get-users', '/user/get-list')
    config.add_route('edit-user', '/user')
    config.add_route('invite', '/user/invite')

    config.add_route('githubdeploy', '/githubdeploy')
    config.scan('.views')
    return config.make_wsgi_app()