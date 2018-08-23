from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render_to_response
from pyramid.view import view_config

from wics_2.models.User import User, UserInvitation
from wics_2.session_manager import SessionManager


session_manager = SessionManager()


session_validation_error = {
    'error': 'It looks like your logged-in session has ended. Log in and try again.'
}

user_validation_error = {
    'error': 'It doesn\'t look like you are a valid user.'
}


def validate_user_session(auth_cookie, db_session):
    username = session_manager.validate_session(auth_cookie)
    if username is None:
        return None, session_validation_error
    user = User.get_user_by_username(username, db_session)
    if user is None:
        return None, user_validation_error
    return user, None


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
        return HTTPFound('/?error=general&message=' + errors)
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
    user, error = validate_user_session(request.cookies.get('session'), request.db_session)
    if error is not None:
        return HTTPFound('/?error=login_error')
    session_manager.refresh_session(request.cookies['session'])
    return {
        'nickname': user.nickname,
        'role_name': user.role.get_role_name(),
    }


@view_config(route_name='get-users', renderer='json')
def get_user_list(request):
    user, error = validate_user_session(request.cookies.get('session'), request.db_session)
    if error is not None:
        return error
    session_manager.refresh_session(request.cookies['session'])
    find_username = request.params.get('username')
    find_email = request.params.get('email')
    users = User.get_by_username_or_email(find_username, find_email, request.db_session)
    if len(users) == 0:
        return {'error': 'No results found!'}
    return {
        'users': list(map(lambda user: user.to_dict(), users))
    }


@view_config(route_name='edit-user', renderer='json', request_method='PATCH')
def promote_user(request):
    user, error = validate_user_session(request.cookies.get('session'), request.db_session)
    if error is not None:
        return error
    if not user.has_permissions_on_others('edit'):
        return {'error': 'You do not have the appropriate permissions to perform this action.'}
    other_username = request.params.get('username')
    if other_username is None:
        return {'error': 'Invalid user was given.'}
    other_user = User.get_user_by_username(other_username, request.db_session)
    if other_user is None:
        return {'error': 'Could not find that user!'}
    if not user.promote_other(other_user, request.db_session):
        return {'error': 'Something went wrong when trying to promote that user!'}
    request.db_session.add(other_user)
    return {'role_name': other_user.role.name}


# Removing a user doesn't pull them from the DB, it sets them to an 'inactive' state
@view_config(route_name='edit-user', renderer='json', request_method='DELETE')
def remove_user(request):
    user, error = validate_user_session(request.cookies.get('session'), request.db_session)
    if error is not None:
        return error
    if not user.has_permissions_on_others('delete'):
        return {'error': 'You do not have the appropriate permissions to perform this action.'}
    del_username = request.params.get('username')
    if del_username is None:
        return {'error': 'Invalid user was given.'}
    del_user = User.get_user_by_username(del_username, request.db_session)
    if del_user is None:
        return {'error': 'Could not find that user!'}
    del_user.active = False
    request.db_session.add(del_user)
    return {'username': del_username}


@view_config(route_name='invite', renderer='json', request_method='POST')
def invite_user(request):
    user, error = validate_user_session(request.cookies.get('session'), request.db_session)
    if error is not None:
        return error
    if not UserInvitation.validate_permissions('create', user):
        return {'error': 'You do not have permission to invite other members'}
    email = request.params.get('email')
    if email is not None:
        email = email.strip()
    if email is None or email == '':
        return {'error': 'Not a valid email!'}
    invite = UserInvitation.create_invite(email, 5, request.db_session)
    return {'link_hash': invite.link_hash}


@view_config(route_name='invite', renderer='json', request_method='GET')
def get_invites(request):
    pass


@view_config(route_name='invite', renderer='json', request_method='DELETE')
def remove_invite(request):
    pass


@view_config(route_name='user-admin', renderer='templates/user_portal/user-admin.jinja2')
def user_admin(request):
    user, error = validate_user_session(request.cookies.get('session'), request.db_session)
    if error is not None:
        return HTTPFound('/?error=general&message={}'.format(error['error']))
    return {'user': user}


@view_config(route_name='blog-admin', renderer='templates/user_portal/blog-admin.jinja2')
def blog_admin(request):
    user, error = validate_user_session(request.cookies.get('session'), request.db_session)
    if error is not None:
        return HTTPFound('/?error=general&message={}'.format(error['error']))
    return {'user': user}


@view_config(route_name='designer', renderer='templates/user_portal/designer.jinja2')
def designer(request):
    user, error = validate_user_session(request.cookies.get('session'), request.db_session)
    if error is not None:
        return HTTPFound('/?error=general&message={}'.format(error['error']))
    return {'user': user}
