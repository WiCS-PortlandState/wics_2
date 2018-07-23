from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render_to_response
from pyramid.view import view_config

from wics_2.models.User import User, UserInvitation
from wics_2.session_manager import SessionManager


session_manager = SessionManager()


@view_config(route_name='login', renderer='json')
def login(request):
    username = request.params.get('username')
    password = request.params.get('password')
    user = User.authenticate(username, password, request.db_session)
    if user is not None:
        return session_manager.create_session(HTTPFound('/user/'), username)
    return HTTPFound('/?error=login_fail')


@view_config(route_name='create-user',
             renderer='./templates/user_portal/auth/create-account.jinja2',
             request_method='GET')
def get_create_user(request):
    invite_hash = request.params.get('invite')
    if invite_hash is None:
        return HTTPFound('/?error=not_invited')
    invite = UserInvitation.validate(invite_hash, request.db_session)
    if invite is None:
        return HTTPFound('/?error=not_invited')
    return {'email': invite.email, 'invite': invite_hash}


@view_config(route_name='create-user', request_method='POST')
def post_create_user(request):
    invite_hash = request.params.get('invite')
    if invite_hash is None:
        return HTTPFound('/?error=not_invited')
    invite = UserInvitation.validate(invite_hash, request.db_session)
    if invite is None:
        return HTTPFound('/?error=not_invited')
    username = request.params.get('username')
    password = request.params.get('password')
    nickname = request.params.get('nickname')
    first_name = request.params.get('first_name')
    last_name = request.params.get('last_name')
    email = request.params.get('email')
    user = User(username, password, first_name, last_name, nickname, email)
    errors = user.get_validation_errors(request.db_session)
    if errors is not None:
        return HTTPFound('/?error=user_create_errors&message=' + errors)
    user.before_save(request.db_session)
    request.db_session.add(user)
    request.db_session.delete(invite)
    return session_manager.create_session(render_to_response(
        './templates/user_portal/home.jinja2',
        {'user': user},
        request=request), username)


@view_config(route_name='logout')
def logout(request):
    session_manager.remove_session(request.cookies['session'])
    return HTTPFound('/')


@view_config(route_name='validate-username', renderer='json')
def validate_username(request):
    username = request.params.get('username')
    user = User.get_user_by_username(username, request.db_session)
    if user is not None:
        return {
            'isTaken': True,
        }
    return {
        'isTaken': False,
    }


@view_config(route_name='user-home', renderer='./templates/user_portal/home.jinja2')
def user_home(request):
    username = session_manager.validate_session(request.cookies['session'])
    if username is None:
        return HTTPFound('/?error=login_error')
    user = User.get_user_by_username(username, request.db_session)
    if user is None:
        return HTTPFound('/?error=login_error')
    session_manager.refresh_session(request.cookies['session'])
    return {
        'nickname': user.nickname,
        'role_name': user.role.get_role_name(),
    }


@view_config(route_name='get-users', renderer='json')
def get_user_list(request):
    username = session_manager.validate_session(request.cookies['session'])
    if username is None:
        return {'error': 'It looks like your logged-in session has ended. Log in and try again.'}
    user = User.get_user_by_username(username, request.db_session)
    if user is None:
        return {'error': 'It looks like your logged-in session has ended. Log in and try again.'}
    session_manager.refresh_session(request.cookies['session'])
    find_username = request.params.get('username')
    find_email = request.params.get('email')
    users = User.get_by_username_or_email(find_username, find_email, request.db_session)
    if len(users) == 0:
        return {'error': 'No results found!'}
    return {
        'users': list(map(lambda user: user.to_dict(), users))
    }
