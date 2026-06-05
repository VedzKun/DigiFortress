import uuid 
class SessionManager:
    def __init__(self):
        self.session_id = str(uuid.uuid4())
    def get_session_id(self):
        return self.session_id
