import logging

from pyramid.view import view_config
from pyramid.response import Response
import subprocess as command
import datetime
import sys
import os

log = logging.getLogger(__name__)


def resolve_error(err):
    if err == 'not_invited':
        return '''
        Sorry! You must be invited to create a WiCS account. 
        If you believe you have an invitation, it may have expired
        '''
    elif err == 'login_error':
        return '''
        It looks like you're not logged in. To access the user portal, 
        you'll need to do that.
        '''
    return None


@view_config(route_name='home', renderer='templates/home.jinja2')
def home(request):
    error = request.params.get('error')
    return {'project': 'wics_2', 'error': resolve_error(error)}


def redeploy():
    base_dir = os.path.dirname(os.path.realpath(__file__))
    process = command.call([base_dir + '/deploy_script.sh'], shell=True)
    if process == 0:
        return True
    else:
        return False


@view_config(route_name='githubdeploy', request_method='POST')
def deploy_prod(request):
    try:
        body = request.json_body
        if 'head_commit' in body and 'ref' in body and 'id' in body['head_commit']:
            if not body['ref'].endswith('master'):
                return Response(content_type = 'text/plain', body = 'no action')
            if redeploy():
                log.debug('Deployment succeeded at ' + datetime.datetime.now().__str__())
                return Response(content_type = 'text/plain', body = 'success')
        log.error('Deployment failed at ' + datetime.datetime.now().__str__())
    except:
        log.error('There was an error handling the request at ' + datetime.datetime.now().__str__())
        log.error(sys.exc_info()[0])
    return Response(content_type='text/plain', body='failed')