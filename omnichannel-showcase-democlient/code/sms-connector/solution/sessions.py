"""
Copyright 2021-present, Nuance, Inc.
All rights reserved.

This source code is licensed under the Apache-2.0 license found in
the LICENSE.md file in the root directory of this source tree.
"""


class SessionStore:
    """
    Mock session store. Currently in-memory.

    Swap this out with a session management solution.
    Key is user_id, and value is the session blob.
    A single user_id maps to a single session.
    """
    def __init__(self):
        self.sessions = {}

    def get_session(self, user_id):
        return self.sessions[user_id] if user_id in self.sessions else None

    def create_session(self, user_id, session):
        self.sessions[user_id] = session
        return session

    def update_session(self, user_id, session):
        self.sessions[user_id] = session
        return session

    def remove_session(self, user_id):
        if user_id in self.session:
            del self.session[user_id]
        return True
