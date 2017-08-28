import uuid
from fuze import db
from fuze import errors
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey
from hashlib import sha256


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class User(db.Model):
    __tablename__ = "user"

    email = db.Column(db.Text, unique=True, primary_key=True, nullable=False)

    recordings = relationship("Recording")
    meetings = relationship("Meeting")

    @classmethod
    def delete(cls, email):
        cls.query.filter(cls.email == email).delete()

    @classmethod
    def create(cls, email):
        if cls.query.filter(cls.email == email).count() > 0:
            raise errors.PreexistingUser

        db.session.add(cls(email=email))
        db.session.commit()

    def __repr__(self):
        return "<User {:s}>".format(self.email)


class Recording(db.Model):
    __tablename__ = "recording"

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text, nullable=False)
    owner_email = db.Column(db.Text, ForeignKey("user.email"))
    public = db.Column(db.Boolean, default=False)
    pwhash = db.Column(db.Text)

    owner = relationship("User", back_populates="recordings")
    viewers = relationship("Viewer")

    @classmethod
    def create(cls, owner, public=False, pw=None):
        url = "{}/{}".format("download", uuid.uuid4().hex)
        if public and pw is None:
            raise errors.PublicPasswordRequired
        elif not public:
            recording = cls(owner_email=owner, url=url)
        else:
            pwhash = sha256(pw.encode("utf-8")).hexdigest()
            recording = cls(
                owner_email=owner, url=url, public=public, pwhash=pwhash
            )

        db.session.add(recording)
        db.session.commit()
        return recording

    @classmethod
    def delete(cls, rid):
        cls.query.filter(cls.id == rid).delete()

    @classmethod
    def share(cls, email, recording):
        if not cls.public:
            raise errors.UserAddToPrivate

        db.session.add(Viewer(viewer=email, recording_id=recording.id))
        db.session.commit()

    @classmethod
    def set_visibility(cls, rid, vis, pw):
        r = cls.query.filter(cls.id == rid).first()
        if r is None:
            raise errors.InvalidRecordingId
        r.public = vis

        db.session.commit()

    def __repr__(self):
        return "<Recording {:s} owner {}>".format(self.url, self.owner)


class Meeting(db.Model):
    __tablename__ = "meeting"

    id = db.Column(db.Integer, primary_key=True)
    host_email = db.Column(db.Text, ForeignKey("user.email"))
    recording_id = db.Column(db.Integer, ForeignKey("recording.id"))

    host = relationship("User", back_populates="meetings")
    recording = relationship("Recording")

    @classmethod
    def create(cls, host, rid):
        meeting = cls(host_email=host, recording_id=rid)
        db.session.add(meeting)
        db.session.commit()
        return meeting

    @classmethod
    def delete(cls, mid, password):
        meeting = cls.query.filter(cls.id == mid).first()
        if meeting is None:
            raise errors.MeetingDoesNotExist(mid)

        if meeting.recording.pwhash is not None and password is not None:
            pwhash = sha256(password.encode("utf-8")).hexdigest()
            assert meeting.recording.pwhash == pwhash, errors.InvalidPassword

        Viewer.query.filter(
            Viewer.id.in_(map(lambda r: r.id, meeting.recording.viewers))
        ).delete(synchronize_session=False)

        cls.query.filter(
            cls.id == mid
        ).delete()

        meeting.recording.delete(meeting.recording.id)

    @classmethod
    def get(cls, meeting):
        if meeting == "all":
            return cls.query.all()
        else:
            return cls.query.filter(cls.id == meeting).first()

    def __repr__(self):
        return "<Meeting host {}>".format(self.host.email)


class Viewer(db.Model):
    __tablename__ = "viewer"

    id = db.Column(db.Integer, primary_key=True)
    viewer = db.Column(db.Text, ForeignKey("user.email"))
    recording_id = db.Column(db.Integer, ForeignKey("recording.id"))

    recording = relationship("Recording", back_populates="viewers")

    @classmethod
    def add(cls, viewer, recording):
        viewer = cls(viewer=viewer.email, recording_id=recording.id)
        db.session.add(viewer)
        db.session.commit()


if __name__ == "__main__":

    db.drop_all()
    db.create_all()
    # s = db.session

    # for user in ["jenny", "jeff", "asad", "jon", "johanna"]:
        # s.add(User(email="{}@foo.com".format(user)))
    # s.commit()

    # for recording, owner_id in [("a", 1), ("b", 2), ("c", 1)]:
        # s.add(Recording(
            # url="http://s3/{}".format(recording),
            # owner_id=owner_id,
            # public=True,
            # pwhash="asdf"
        # ))
    # s.commit()

    # s.add(Viewer(viewer="jeff@foo.com", recording=1))
    # s.add(Viewer(viewer="asad@foo.com", recording=1))
    # s.add(Viewer(viewer="jon@foo.com", recording=1))
    # s.add(Viewer(viewer="johanna@foo.com", recording=1))
    # s.commit()

    # User.delete(2)
