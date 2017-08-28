import requests
import pprint
import base64
import json

from fuze.models import db
db.drop_all()
db.create_all()

url = "http://localhost:5000{}"

print("Let's create some users")
for user in ["bender", "fry", "amy", "leela", "zoidberg"]:
    print("Adding user {}".format(user))
    resp = requests.post(
        url.format("/user"),
        data=json.dumps({"email": "{}@planetexpress.com".format(user)})
    )
    assert resp.status_code == 200

print("Bender should only be allowed to create one account in his name")
resp = requests.post(
    url.format("/user"),
    data=json.dumps({"email": "{}@planetexpress.com".format("bender")})
)
assert resp.status_code == 409

print("Let's go ahead and create a meeting")
resp = requests.post(
    url.format("/meeting"),
    data=json.dumps({
        "host": "leela@planetexpress.com",
        "password": "nibbler"
    })
)

assert resp.status_code == 200

print("Let's get a list of all meetings")
resp = requests.get(
    url.format("/meeting"),
    params={"meeting_id": "all"}
)
pprint.pprint(resp.json())


print("Fry is going to try and view the meeting without being a viewer")
auth = base64.b64encode("fry@planetexpress.com:nibbler".encode("utf-8"))
headers = {
    "Authorization": "Basic {}".format(auth.decode("ascii"))
}
resp = requests.get(
    url.format("/view"),
    params={"meeting_id": 1},
    headers=headers
)
assert resp.status_code == 401

print("Let's add Fry to the meeting")
resp = requests.put(
    url.format("/meeting"),
    data=json.dumps({
        "meeting_id": 1,
        "email": "fry@planetexpress.com"
    })
)
assert resp.status_code == 200


print("Let's try viewing again")
resp = requests.get(
    url.format("/view"),
    params={"meeting_id": 1},
    headers=headers
)
assert resp.status_code == 200

print("Delete the meeting")
resp = requests.delete(
    url.format("/meeting"),
    data=json.dumps({
        "meeting_id": 1
    })
)
assert resp.status_code == 200
