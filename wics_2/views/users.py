import os
import hashlib
import uuid
import sched, time

import random
import datetime

from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render_to_response
from pyramid.session import signed_serialize
from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound

from wics_2.models.User import Salt, User, Role
from wics_2.models.UserInvitations import UserInvitations


def get_user(username, session):
    try:
        user = session.query(User).filter(User.username == username).one()
    except NoResultFound:
        user = None
    return user


def get_default_user_role(session):
    try:
        role = session.query(Role).filter(Role.member).one()
    except NoResultFound:
        role = None
    return role


def authenticate_user(username, password, session):
    user = get_user(username, session)
    if user is not None:
        salt = session.query(Salt).filter(Salt.id == user.salt).one()
        salted = (password + salt.value).encode('utf8')
        hashed_pw = hashlib.sha512(salted).hexdigest()
        if user.password == hashed_pw:
            return user
    return None


def validate_invitation(invite_hash, session):
    try:
        invite = session.query(UserInvitations).filter(UserInvitations.link_hash == invite_hash).one()
    except NoResultFound:
        invite = None
    if invite is not None and datetime.datetime.utcnow() <= invite.expire_date:
        return invite
    return None


def salt_password(pw, session):
    salts = session.query(Salt).all()
    salt = random.choice(salts)
    salted = (pw + salt.value).encode('utf8')
    return hashlib.sha512(salted).hexdigest(), salt.id


sessions = dict()
scheduler = sched.scheduler(time.time, time.sleep)


def cleanup_sessions():
    now = datetime.datetime.now()
    for (key, val) in sessions:
        if val['expires'] < now:
            del sessions[key]
    scheduler.enter(60, 2, cleanup_sessions)


scheduler.enter(60, 2, cleanup_sessions)


def create_session(response, username):
    cookie_val = signed_serialize({'session': uuid.uuid4().hex}, os.getenv('WICS_SECRET', '1h3$L6'))
    response.set_cookie('session', cookie_val)
    sessions[cookie_val] = {
        'expires': datetime.datetime.now() + datetime.timedelta(minutes=15),
        'user': username,
    }
    return response


def refresh_session(cookie_val):
    found = sessions.get(cookie_val)
    if found is not None:
        found['expires'] += datetime.timedelta(minutes=15)
        return True
    return False


def validate_session(cookie_val):
    found = sessions.get(cookie_val)
    if found is not None:
        return found['user']
    return None


def remove_session(cookie_val):
    found = sessions.get(cookie_val)
    if found is not None:
        del sessions[cookie_val]
        return True
    return False


@view_config(route_name='login', renderer='json')
def login(request):
    username = request.params.get('username')
    password = request.params.get('password')
    user = authenticate_user(username, password, request.dbsession)
    if user is not None:
        return create_session(HTTPFound('/user/'), username)
    return HTTPFound('/?error=login_fail')


@view_config(route_name='create-user',
             renderer='./templates/user_portal/auth/create-account.jinja2',
             request_method='GET')
def get_create_user(request):
    invite_hash = request.params.get('invite')
    if invite_hash is None:
        return HTTPFound('/?error=not_invited')
    invite = validate_invitation(invite_hash, request.dbsession)
    if invite is None:
        return HTTPFound('/?error=not_invited')
    return {'email': invite.email, 'invite': invite_hash}


@view_config(route_name='create-user', request_method='POST')
def post_create_user(request):
    invite_hash = request.params.get('invite')
    if invite_hash is None:
        return HTTPFound('/?error=not_invited')
    invite = validate_invitation(invite_hash, request.dbsession)
    if invite is None:
        return HTTPFound('/?error=not_invited')
    username = request.params.get('username')
    password = request.params.get('password')
    nickname = request.params.get('nickname')
    first_name = request.params.get('first_name')
    last_name = request.params.get('last_name')
    email = request.params.get('email')
    (password, salt) = salt_password(password, request.dbsession)
    user = User()
    user.username = username
    user.password = password
    user.salt = salt
    user.role = get_default_user_role(request.dbsession).id
    user.nickname = nickname
    user.first_name = first_name
    user.last_name = last_name
    user.email = email
    request.dbsession.add(user)
    request.dbsession.delete(invite)
    return create_session(render_to_response(
        './templates/user_portal/home.jinja2',
        {'user': user},
        request=request), username)


@view_config(route_name='logout')
def logout(request):
    remove_session(request.cookies['session'])
    return HTTPFound('/')


@view_config(route_name='validate-username', renderer='json')
def validate_username(request):
    username = request.params.get('username')
    user = get_user(username, request.dbsession)
    if user is not None:
        return {
            'isTaken': True,
        }
    return {
        'isTaken': False,
    }


@view_config(route_name='user-home', renderer='./templates/user_portal/home.jinja2')
def user_home(request):
    username = validate_session(request.cookies['session'])
    if username is None:
        return HTTPFound('/?error=login_error')
    user = get_user(username, request.dbsession)
    # if user is None:
    #     return HTTPFound('/?error=login_error')
    return {
        'nickname': 'whatever'
    }
