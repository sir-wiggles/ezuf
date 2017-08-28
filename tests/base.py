import unittest
import json

from fuze import app, db
from fuze.app import configure

configure(app, db)


class DatabaseMixin(unittest.TestCase):

    def setUp(self):

        self.app_context = app.app_context()
        self.app_context.push()

        self.app = app.test_client()
        self.app.application.config["TESTING"] = True
        self.app.application.config["SQLALCHEMY_ECHO"] = False
        self.app.application.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///"

        self.db = db
        self.db.drop_all()
        self.db.create_all()

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()
        self.app_context.pop()


class HelperMixin(unittest.TestCase):

    def setUp(self):
        super(HelperMixin, self).setUp()

    def tearDown(self):
        super(HelperMixin, self).tearDown()

    def call(self, method, url, qs=None, data=None, headers=None):
        data = json.dumps(data) if data else None

        if not headers:
            headers = {"content-type": "application/json"}

        resp = getattr(self.app, method)(
            url,
            data=data,
            headers=headers,
            query_string=qs,
        )
        return json.loads(resp.data.decode("ascii")), resp.status_code, resp.headers
