import base64
from hashlib import sha256
from fuze.models import Meeting, Recording, User, Viewer
from tests.base import DatabaseMixin, HelperMixin


class UserTests(DatabaseMixin, HelperMixin):

    def setUp(self):
        super(UserTests, self).setUp()
        self.db.session.add(User(email="test@foo.com"))
        self.db.session.commit()

    def tearDown(self):
        super(UserTests, self).tearDown()

    def test_health(self):
        resp, code, headers = self.call("get", "/health")
        self.assertEqual(code, 200)

    def test_user_create_simple(self):
        data = {"email": "test2@foo.com"}
        resp, code, headers = self.call("post", "/user", data=data)
        self.assertEqual(code, 200, resp)

        user = self.db.session.query(User).filter(
            User.email == "test2@foo.com"
        ).all()
        self.assertEqual(len(user), 1)

    def test_user_create_preexisting(self):
        data = {"email": "test@foo.com"}
        resp, code, headers = self.call("post", "/user", data=data)
        self.assertEqual(code, 409, resp)

        user = self.db.session.query(User).filter(
            User.email == "test@foo.com"
        ).all()
        self.assertEqual(len(user), 1)

    def test_user_delete(self):
        data = {"email": "test@foo.com"}
        resp, code, headers = self.call("delete", "/user", data=data)
        self.assertEqual(code, 200, resp)

        user = self.db.session.query(User).filter(
            User.email == "test@foo.com"
        ).all()
        self.assertEqual(len(user), 0)


class MeetingTests(DatabaseMixin, HelperMixin):

    def setUp(self):
        super(MeetingTests, self).setUp()

        self.user = User(email="test@foo.com")
        self.db.session.add(self.user)
        self.db.session.commit()

    def tearDown(self):
        super(MeetingTests, self).tearDown()

    def test_meeting_create_simple(self):

        data = {
            "host": "test@foo.com",
        }
        resp, code, headers = self.call("post", "/meeting", data=data)
        self.assertEqual(code, 200, resp)

        mid = resp["meeting_id"]
        meeting = self.db.session.query(Meeting).filter(
            Meeting.id == mid
        ).all()
        self.assertEqual(len(meeting), 1)

        recordings = self.db.session.query(Recording).all()
        self.assertEqual(len(recordings), 1)

        viewers = self.db.session.query(Viewer).all()
        self.assertEqual(len(viewers), 1)

    def test_meeting_create_two_same_user(self):

        data = {
            "host": "test@foo.com",
        }
        resp, code, headers = self.call("post", "/meeting", data=data)
        self.assertEqual(code, 200, resp)

        resp, code, headers = self.call("post", "/meeting", data=data)
        self.assertEqual(code, 200, resp)

        meeting = self.db.session.query(Meeting).all()
        self.assertEqual(len(meeting), 2)

        recordings = self.db.session.query(Recording).all()
        self.assertEqual(len(recordings), 2)

        viewers = self.db.session.query(Viewer).all()
        self.assertEqual(len(viewers), 2)

    def test_meeting_delete(self):

        recording = Recording(owner_email=self.user.email, url="test")
        self.db.session.add(recording)
        self.db.session.commit()

        meeting = Meeting(host_email="test@foo.com", recording_id=recording.id)
        self.db.session.add(meeting)
        self.db.session.commit()

        self.db.session.add(Viewer(
            viewer=meeting.host.email, recording_id=recording.id
        ))
        self.db.session.commit()

        data = {
            "meeting_id": meeting.id
        }
        resp, code, headers = self.call("delete", "/meeting", data=data)
        self.assertEqual(code, 200, resp)

        meetings = self.db.session.query(Meeting).all()
        recordings = self.db.session.query(Recording).all()
        viewers = self.db.session.query(Viewer).all()
        self.assertEqual(len(meetings), 0)
        self.assertEqual(len(recordings), 0)
        self.assertEqual(len(viewers), 0)

    def test_meeting_list(self):

        recording = Recording(owner_email=self.user.email, url="test")
        self.db.session.add(recording)
        self.db.session.commit()

        meeting = Meeting(host_email="test@foo.com", recording_id=recording.id)
        self.db.session.add(meeting)
        self.db.session.commit()

        self.db.session.add(Viewer(
            viewer=meeting.host.email, recording_id=recording.id
        ))
        self.db.session.commit()

        qs = {"meeting_id": "all"}
        resp, code, headers = self.call("get", "/meeting", qs=qs)
        self.assertEqual(code, 200, resp)
        self.assertEqual(len(resp["results"]), 1)

    def test_meeting_get(self):

        recording = Recording(owner_email=self.user.email, url="test")
        self.db.session.add(recording)
        self.db.session.commit()

        meeting = Meeting(host_email="test@foo.com", recording_id=recording.id)
        self.db.session.add(meeting)
        self.db.session.commit()

        self.db.session.add(Viewer(
            viewer=meeting.host.email, recording_id=recording.id
        ))
        self.db.session.commit()

        qs = {"meeting_id": 1}
        resp, code, headers = self.call("get", "/meeting", qs=qs)
        self.assertEqual(code, 200, resp)
        self.assertEqual(resp["meeting"]["id"], 1)

    def test_meeting_delete_dne(self):

        recording = Recording(owner_email=self.user.email, url="test")
        self.db.session.add(recording)
        self.db.session.commit()

        meeting = Meeting(host_email="test@foo.com", recording_id=recording.id)
        self.db.session.add(meeting)
        self.db.session.commit()

        self.db.session.add(Viewer(
            viewer=meeting.host.email, recording_id=recording.id
        ))
        self.db.session.commit()

        data = {"meeting_id": 100}
        resp, code, headers = self.call("delete", "/meeting", data=data)
        self.assertEqual(code, 404, resp)

        meetings = self.db.session.query(Meeting).all()
        recordings = self.db.session.query(Recording).all()
        viewers = self.db.session.query(Viewer).all()
        self.assertEqual(len(meetings), 1)
        self.assertEqual(len(recordings), 1)
        self.assertEqual(len(viewers), 1)

    def test_meeting_share(self):
        self.user = User(email="test2@foo.com")
        self.db.session.add(self.user)
        self.db.session.commit()

        recording = Recording(owner_email=self.user.email, url="test")
        self.db.session.add(recording)
        self.db.session.commit()

        meeting = Meeting(host_email="test@foo.com", recording_id=recording.id)
        self.db.session.add(meeting)
        self.db.session.commit()

        self.db.session.add(Viewer(
            viewer=meeting.host.email, recording_id=recording.id
        ))
        self.db.session.commit()

        data = {
            "meeting_id": meeting.id,
            "email": "test2@foo.com"
        }
        resp, code, headers = self.call("put", "/meeting", data=data)
        self.assertEqual(code, 200, resp)

        meetings = self.db.session.query(Meeting).all()
        recordings = self.db.session.query(Recording).all()
        viewers = self.db.session.query(Viewer).all()
        self.assertEqual(len(meetings), 1)
        self.assertEqual(len(recordings), 1)
        self.assertEqual(len(viewers), 2)

    def test_meeting_view_with_access(self):

        self.user = User(email="test2@foo.com")
        self.db.session.add(self.user)
        self.db.session.commit()

        pwhash = sha256(
            "secret".encode("utf-8")
        ).hexdigest()

        recording = Recording(
            owner_email=self.user.email, url="/view_recording/asdf",
            public=True, pwhash=pwhash
        )
        self.db.session.add(recording)
        self.db.session.commit()

        meeting = Meeting(host_email="test@foo.com", recording_id=recording.id)
        self.db.session.add(meeting)
        self.db.session.commit()

        self.db.session.add(Viewer(
            viewer=meeting.host.email, recording_id=recording.id
        ))
        self.db.session.commit()

        self.db.session.add(Viewer(
            viewer="test2@foo.com", recording_id=recording.id
        ))
        self.db.session.commit()

        pwb64 = base64.b64encode(
            "test@foo.com:secret".encode("utf-8")
        ).decode("ascii")
        headers = {
            "Authorization": "Basic {}".format(pwb64)
        }
        qs = {"meeting_id": 1}
        resp, code, headers = self.call("get", "/view", headers=headers, qs=qs)
        self.assertEqual(code, 302, resp)
        self.assertTrue(
            "view_recording/asdf" in headers.get("Location")
        )

    def test_meeting_view_without_access(self):

        self.user = User(email="test2@foo.com")
        self.db.session.add(self.user)
        self.db.session.commit()

        pwhash = sha256(
            "secret".encode("utf-8")
        ).hexdigest()

        recording = Recording(
            owner_email=self.user.email, url="test", public=True, pwhash=pwhash
        )
        self.db.session.add(recording)
        self.db.session.commit()

        meeting = Meeting(host_email="test@foo.com", recording_id=recording.id)
        self.db.session.add(meeting)
        self.db.session.commit()

        self.db.session.add(Viewer(
            viewer=meeting.host.email, recording_id=recording.id
        ))
        self.db.session.commit()

        self.db.session.add(Viewer(
            viewer="test2@foo.com", recording_id=recording.id
        ))
        self.db.session.commit()

        pwb64 = base64.b64encode(
            "test2@foo.com:foobar".encode("utf-8")
        ).decode("ascii")
        headers = {
            "Authorization": "Basic {}".format(pwb64)
        }
        qs = {"meeting_id": 1}
        resp, code, _ = self.call("get", "/view", headers=headers, qs=qs)
        self.assertEqual(code, 401)

    def test_meeting_view_with_pw_but_not_viewer(self):

        pwhash = sha256(
            "secret".encode("utf-8")
        ).hexdigest()

        recording = Recording(
            owner_email=self.user.email, url="test", public=True, pwhash=pwhash
        )
        self.db.session.add(recording)
        self.db.session.commit()

        meeting = Meeting(host_email="test@foo.com", recording_id=recording.id)
        self.db.session.add(meeting)
        self.db.session.commit()

        self.db.session.add(Viewer(
            viewer=meeting.host.email, recording_id=recording.id
        ))
        self.db.session.commit()

        pwb64 = base64.b64encode(
            "test2@foo.com:secret".encode("utf-8")
        ).decode("ascii")
        headers = {
            "Authorization": "Basic {}".format(pwb64)
        }
        qs = {"meeting_id": 1}
        resp, code, _ = self.call("get", "/view", headers=headers, qs=qs)
        self.assertEqual(code, 401)


class RecordingTests(DatabaseMixin, HelperMixin):

    def setUp(self):
        super(RecordingTests, self).setUp()
        self.user = User(email="test@foo.com")
        self.db.session.add(self.user)
        self.db.session.commit()

    def tearDown(self):
        super(RecordingTests, self).tearDown()

    def test_recording_set_private(self):

        pwhash = sha256(
            "secret".encode("utf-8")
        ).hexdigest()

        recording = Recording(
            owner_email=self.user.email, url="test", public=True, pwhash=pwhash
        )
        self.db.session.add(recording)
        self.db.session.commit()

        data = {
            "recording_id": 1,
            "visibility": "private",
        }
        resp, code, _ = self.call("put", "/recording", data=data)
        self.assertEqual(code, 200)

        rec = Recording.query.filter(Recording.id == 1).first()
        self.assertFalse(rec.public)

    def test_recording_set_public(self):

        pwhash = sha256(
            "secret".encode("utf-8")
        ).hexdigest()

        recording = Recording(
            owner_email=self.user.email, url="foo", public=False, pwhash=pwhash
        )
        self.db.session.add(recording)
        self.db.session.commit()

        data = {
            "recording_id": 1,
            "visibility": "public",
            "password": "foobar",
        }
        resp, code, _ = self.call("put", "/recording", data=data)
        self.assertEqual(code, 200)

        rec = Recording.query.filter(Recording.id == 1).first()
        self.assertTrue(rec.public)
