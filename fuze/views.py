from hashlib import sha256
from functools import wraps
from flask import request, redirect
from fuze import errors
from fuze.models import Meeting, Recording, User, Viewer
from fuze.scheme import mapping
from jsonschema import validate
from jsonschema.exceptions import ValidationError


PUBLIC = "public"
PRIVATE = "private"


def health():
    return {"message": ":D"}, 200


def payload_validation(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        payload = request.get_json(force=True)

        try:
            validate(payload, mapping[func.__name__])
        except ValidationError as e:
            raise errors.SchemaValidationError(e.message)

        return func(**payload)
    return wrapper


def valid_credentials(username, password):
    meeting_id = request.args.get("meeting_id")
    if meeting_id.isdigit():
        meeting_id = int(meeting_id)
    else:
        raise errors.InvalidMeetingId

    meeting = Meeting.get(meeting_id)
    if not meeting:
        raise errors.InvalidCredentials

    pwhash = sha256(password.encode("utf-8")).hexdigest()
    if meeting.recording.pwhash != pwhash:
        return False

    if not meeting.recording.public:
        if meeting.recording.owner == username:
            return True
    else:
        for v in meeting.recording.viewers:
            if v.viewer == username:
                return True
        return False


def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth = request.authorization
        step1 = not auth.username or not auth.password
        step2 = not valid_credentials(auth.username, auth.password)
        if (step1 or step2):
            raise errors.InvalidCredentials
        meeting_id = int(request.args.get("meeting_id"))
        return func(meeting_id)
    return wrapper


@payload_validation
def user_create(email):
    User.create(email)
    return {"message": "user created"}, 200


@payload_validation
def user_delete(email):
    User.delete(email)
    return {}, 200


@payload_validation
def meeting_create(host, password=None):
    public = True if password else False
    recording = Recording.create(host, public, password)
    meeting = Meeting.create(host, recording.id)
    Viewer.add(meeting.host, recording)
    return {
        "meeting_id": meeting.id,
        "recording_url": recording.url,
    }, 200


@payload_validation
def meeting_delete(meeting_id, password=None):
    Meeting.delete(meeting_id, password)
    return {}, 200


@payload_validation
def meeting_share(meeting_id, email):
    meeting = Meeting.get(meeting_id)
    meeting.recording.share(email, meeting.recording)
    return {}, 200


def meeting_get():

    def fmt(meeting):
        return {
            "meeting": {
                "id": meeting.id,
                "host": meeting.host.email
            },
            "recording": {
                "id": meeting.recording.id,
            },
            "viewers": list(map(lambda v: v.viewer, meeting.recording.viewers))
        }
    meeting_id = request.args.get("meeting_id", "all")

    if meeting_id == "all":
        meetings = Meeting.get(meeting_id)
        resp = []
        for meeting in meetings:
            resp.append(fmt(meeting))
        return {"results": resp}, 200
    else:
        if meeting_id.isdigit():
            meeting_id = int(meeting_id)
        else:
            raise errors.InvalidMeetingId
        meeting = Meeting.get(meeting_id)
        return fmt(meeting), 200


@authenticate
def meeting_view(mid):
    meeting = Meeting.get(mid)
    resp = redirect(meeting.recording.url, 302)
    resp.data = '{}'
    resp.headers["Content-Type"] = "application/json"
    return resp


def download(recording_id):
    return {"redirected": "to s3 to get your recording"}, 200


@payload_validation
def recording_visibility(recording_id, visibility, password=None):

    if visibility == PUBLIC:
        visibility = True
    elif visibility == PRIVATE:
        visibility = False
    else:
        visibility = False

    Recording.set_visibility(recording_id, visibility, password)
    return {}, 200
