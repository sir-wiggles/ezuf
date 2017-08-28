import werkzeug.exceptions as ex


class PreexistingUser(ex.HTTPException):
    code = 409
    description = "A user with that email already exists"


class InvalidPassword(ex.HTTPException):
    code = 401
    description = "Password required"


class UserAddToPrivate(ex.HTTPException):
    code = 401
    description = "Can't add user to recording while recording is private"


class MeetingDoesNotExist(ex.HTTPException):
    code = 404
    description = "Meeting with that id does not exist"


class InvalidMeetingId(ex.HTTPException):
    code = 400
    description = "Meeting id must be an int or 'all'"


class InvalidRecordingId(ex.HTTPException):
    code = 404
    description = "Recording id not found"


class InvalidCredentials(ex.HTTPException):
    code = 401
    description = "Invalid username or password"


class SchemaValidationError(ex.HTTPException):
    code = 400

    def __init__(self, message):
        super(SchemaValidationError, self).__init__(description=message)

