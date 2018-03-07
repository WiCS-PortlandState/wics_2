from pyramid.view import view_config


@view_config(route_name='home', renderer='templates/home.jinja2')
def home(request):
    return {'project': 'wics_2'}


@view_config(route_name='hackathon-home', renderer='templates/hackathon-home.jinja2')
def hackathon_home(request):
    return {'project': 'hackathon'}
