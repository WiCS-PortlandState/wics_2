import bcrypt
import random

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound

from wics_2.models.User import Salt, User
from ..models.meta import DBSession


def authenticate_user(username, password, session):
    try:
        user = session.query(User).filter(User.username == username).one()
    except NoResultFound:
        user = None
    if user is not None:
        salt = session.query(Salt).filter(Salt.id == user.salt).one()
        hashed_pw = bcrypt.hashpw(password.encode('utf8'), salt.value).decode('utf8')
        if user.password == hashed_pw:
            return user
    return None


def salt_password(pw):
    salts = DBSession.query(Salt).all()
    salt = random.choice(salts)
    return bcrypt.hashpw(pw.encode('utf8'), salt.value).decode('utf8'), salt.id


@view_config(route_name='login', renderer='json')
def login(request):
    username = request.params['username']
    password = request.params['password']
    user = authenticate_user(username, password, request.dbsession)
    if user is not None:
        request.session['wics2'] = user.username
        request.session.save()
        HTTPFound('user-home')
    return {
        'error': {
            'message': 'Incorrect username or password',
        },
    }


@view_config(route_name='create-user', renderer='json')
def create_user(request):
    user = User()
    user.first_name = request.params['firstName']
    user.last_name = request.params['lastName']
    user.nickname = request.params['nickname']
    user.password, user.salt = salt_password(request.params['password'])
    user.username = request.params['username']
    request.dbsession.add(user)


@view_config(route_name='logout')
def logout(request):
    request.session.invalidate()
    return HTTPFound('home')


@view_config(route_name='validate-username', renderer='json')
def validate_username(request):
    username = request.params['username']
    user = get_user(username)
    if user is not None:
        return {
            'isTaken': True,
        }
    return {
        'isTaken': False,
    }
