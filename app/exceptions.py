class AppBaseException(Exception):
    def __init__(self, details: str):
        self.details = details
        super().__init__(details)

class UserNotFound(AppBaseException):
    pass

class InvalidSession(AppBaseException):
    pass

class InvalidCode(AppBaseException):
    pass

class FilePermissionError(AppBaseException):
    pass

class FileNotFound(AppBaseException):
    pass