import datetime
import os
import sched
import time
import uuid

from pyramid.session import signed_serialize


class SessionManager(object):
    instance = None

    def __new__(cls):
        if not SessionManager.instance:
            SessionManager.instance = SessionManager.__SessionManager()
        return SessionManager.instance

    def __getattr__(self, item):
        return getattr(self.instance, item)

    def __setattr__(self, key, value):
        return setattr(self.instance, key, value)

    class __SessionManager(object):
        sessions = dict()
        scheduler = sched.scheduler(time.time, time.sleep)

        def __init__(self):
            self.scheduler.enter(60, 2, self.cleanup_sessions)

        def cleanup_sessions(self):
            now = datetime.datetime.now()
            for (key, val) in self.sessions:
                if val['expires'] < now:
                    del self.sessions[key]
            self.scheduler.enter(60, 2, self.cleanup_sessions)

        def create_session(self, response, username):
            cookie_val = signed_serialize({'session': uuid.uuid4().hex}, os.getenv('WICS_SECRET', '1h3$L6'))
            response.set_cookie('session', cookie_val)
            self.sessions[cookie_val] = {
                'expires': datetime.datetime.now() + datetime.timedelta(minutes=15),
                'user': username,
            }
            return response

        def refresh_session(self, cookie_val):
            found = self.sessions.get(cookie_val)
            if found is not None:
                found['expires'] += datetime.timedelta(minutes=15)
                return True
            return False

        def validate_session(self, cookie_val):
            found = self.sessions.get(cookie_val)
            if found is not None:
                return found['user']
            return None

        def remove_session(self, cookie_val):
            found = self.sessions.get(cookie_val)
            if found is not None:
                del self.sessions[cookie_val]
                return True
            return False
