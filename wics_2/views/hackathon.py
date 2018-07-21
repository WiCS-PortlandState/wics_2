from pyramid.view import view_config
import logging



log = logging.getLogger(__name__)


@view_config(route_name='hackathon-home', renderer='templates/hackathon/hackathon-home.jinja2')
def hackathon_home(request):
    return {'project': 'hackathon'}


@view_config(route_name='hackathon-schedule', renderer='templates/hackathon/hackathon-schedule.jinja2')
def hackathon_schedule(request):
    return {'project': 'hackathon'}


@view_config(route_name='hackathon-register', renderer='templates/hackathon/hackathon-register.jinja2')
def hackathon_register(request):
    return {'project': 'hackathon'}


@view_config(route_name='hackathon-contact', renderer='templates/hackathon/hackathon-contact.jinja2')
def hackathon_contact(request):
    return {'project': 'hackathon'}


@view_config(route_name='hackathon-sponsors', renderer='templates/hackathon/hackathon-sponsors.jinja2')
def hackathon_sponsors(request):
    return {'project': 'hackathon'}


@view_config(route_name='designer-home', renderer='templates/designer/home.jinja2')
def designer_home(request):
    return {'project': 'designer'}



