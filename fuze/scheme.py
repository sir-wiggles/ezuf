_user_create = {
    "type": "object",
    "properties": {
        "email": {
            "type": "string",
            "description": "email of the user you are creating",
            "format": "email",
        }
    },
    "required": ["email"]
}

_user_delete = {
    "type": "object",
    "properties": {
        "email": {
            "type": "string",
            "description": "email of the user you are deleting",
            "format": "email",
        }
    },
    "required": ["email"]
}

_meeting_create = {
    "type": "object",
    "properties": {
        "host": {
            "type": "string",
            "description": "the users email creating this meeting",
            "format": "email",
        },
        "password": {
            "type": "string",
            "description": "password for public recording"
        }
    },
    "required": ["host"]
}

_meeting_delete = {
    "type": "object",
    "properties": {
        "meeting_id": {
            "type": "number",
            "description": "the id of the meeting to delete",
            "minimum": 0,
        },
        "password": {
            "type": "string",
            "description": "password for public recording"
        }
    },
    "required": ["meeting_id"]
}

_meeting_share = {
    "type": "object",
    "properties": {
        "meeting_id": {
            "type": "number",
            "description": "id of the meeting you want to share",
            "minimum": 0,
        },
        "email": {
            "type": "string",
            "description": "email of the user you want to share with",
            "format": "email",
        }
    },
    "required": ["meeting_id", "email"]
}

_meeting_get = {
    "type": "object",
    "properties": {
        "meeting_id": {
            "type": ["number", "string"],
            "description": "id of the meeting want or all for all meetings",
            "minimum": 0,
        }
    }
}

_recording_visibility = {
    "type": "object",
    "properties": {
        "recording_id": {
            "type": "number",
            "description": "recording id you want to change visibility on",
            "minimum": 0,
        },
        "password": {
            "type": "string",
            "description": "password you want to set on the recording"
        },
        "visibility": {
            "type": "string",
            "enum": ["public", "private"]
        },
    },
    "required": ["recording_id", "visibility"]
}

mapping = {
    "user_create": _user_create,
    "user_delete": _user_delete,

    "meeting_create": _meeting_create,
    "meeting_delete": _meeting_delete,
    "meeting_share": _meeting_share,
    "meeting_get": _meeting_get,

    "recording_visibility": _recording_visibility
}
