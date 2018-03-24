from pyramid.view import view_config
import subprocess as command
import logging
import datetime
log = logging.getLogger(__name__)


@view_config(route_name='home', renderer='templates/home.jinja2')
def home(request):
    return {'project': 'wics_2'}


@view_config(route_name='hackathon-home', renderer='templates/hackathon-home.jinja2')
def hackathon_home(request):
    return {'project': 'hackathon'}


def self_is_outdated(commit):
    process = command.Popen(['git rev-parse HEAD'], stdout=command.PIPE, shell=True)
    (output, err) = process.communicate()
    if process.wait() == 0:
        return commit[:len(commit) - 1].decode('utf-8') == output
    return False


def redeploy():
    process = command.Popen(['git pull origin master'])
    process.communicate()
    if process.wait() == 0:
        log.debug('Deploying from Github master at ' + datetime.datetime.now().__str__())
    else:
        log.error('Error deploying from master')


@view_config(route_name='githubdeploy', request_method='POST')
def deploy_prod(request):
    body = request.json_body
    if 'head_commit' in body and 'id' in body['head_commit']:
        if self_is_outdated(body['head_commit']['id']):
            redeploy()
