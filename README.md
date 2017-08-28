# Fuze coding challenge 

#### If using `Docker` + `Docker Compose`
1. In the root directory execute `$ docker-compose up`
2. Wait for the containers to build
3. You should see some logs similar to 
```
app_1  | [2017-08-28 08:02:33 +0000] [1] [INFO] Starting gunicorn 19.7.1
app_1  | [2017-08-28 08:02:33 +0000] [1] [INFO] Listening at: http://0.0.0.0:80 (1)
app_1  | [2017-08-28 08:02:33 +0000] [1] [INFO] Using worker: sync
app_1  | [2017-08-28 08:02:33 +0000] [8] [INFO] Booting worker with pid: 8
```
4. The server should be up and running on port `5000`
5. Handling the database
    a. Initialize execute `$ docker exec fuze_app_1 python3 -c "from fuze.models import *; db.create_all()"`
    b. Recreate execute `$ docker exec fuze_app_1 python3 -c "from fuze.models import *; db.drop_all(); db.create_all()"`
6. Should now be able to make curl calls to `localhost:5000/<API>`

#### If not using `Docker` + `Docker Compose`
1. Developed with `Python3` using `Flask` and `Flask-SqlAlchemy` please run `pip3 install -r requirements.txt` to install needed modules
2a. To initialize the data base execute `python3 -c "from fuze.models import *; db.create_all()"` from within the root directory.
2b. The DB given in the pachage should be setup and ready to go if you don't want to run `2a`
3. To start the server run `python3 run.py`.  The server should be running on port `5000`
4. The app should be self contained except for the external call to S3 which is just redirecting to an internal endpiont in place of S3. 
5. `pyhton story.py` runs through an example scenario although not complete in using all endpoints. For examples of using all endpoints please refer to the tests
6. To run the tests execute `nosetests tests/*`


#### Overall project scructure

```
.
├── config.py         # application settings
├── fuze              # root dir of the application
│   ├── __init__.py   # initializes application and database connections
│   ├── app.py        # application routing configuration
│   ├── errors.py     # application defined errors
│   ├── models.py     # database schemes 
│   ├── scheme.py     # json validation schemes 
│   └── views.py      # route handlers
├── fuze.db           # application database configurable through config
├── README.md
├── requirements.txt  # dependencies for the application
├── run.py            # to start the server on 5050 or overwrite in config
├── story.py          # example using the endpoints
└── tests             # application tests 
    ├── __init__.py  
    ├── base.py       # database and helper class mixins
    └── views.py      # tests for views
```

# API 

#### `GET    /health` 
Simple server health check with resp 200

#### `POST   /user` 
Creates a user 
    Parameters:
      email (required) string (email)

#### `DELETE /user` 
removes a user from the database
    Parameters:
      email (required) string (email)

#### `POST   /meeting` 
creates a new meeting with a recording as private.  If a password is given then the recording with be marked as public
    Parameters:
      host  (required) string (email)
      password (optional) string

#### `DELETE /meeting` 
removes a meeting
    Parameters:
      meeting_id (required) int 

#### `PUT    /meeting` 
shares a recording with another user
    Parameters:
      meeting_id (required) int
      email      (required) string (email) *email of the user you want to share with*

#### `GET    /meeting` 
get a meeting information
    Query Parameters:
      meeting_id: (optional) [int, "all"] returns a single meeting if meeting_id is an int or a list of meetings, default to all

#### `GET    /view` 
to view a meeting's recording
    Query Parameters:
      meeting_id: (required) int The id of the meeting recording you want to view
    Headers:
      "Authorization": "Basic {}".format(base64(username:password))

#### `PUT /recording`
set the visibility on the recording to either public or private
    Query Parameters:
      recording_id: (required) int The id of the recording you want to update
      visibility: (required) string Either public or private
      
      
# DB

The `meeting` is really center to everyting.  When you create a `meeting` a `recording` will be attached to it.  Also the `user` that created the `meeting` will be attached to the `recording` as the `owner` and as an authorized `viewer`

When you want to `share` a `recording` you share the `meeting` with a `user` email. They will then be added to the `viewer` table with the `recording` of the meeting. 

Also, `PRAGMA foreign-keys=ON` is set on every connection to enable `FOREIGN KEY` constraints.

```sql
CREATE TABLE user (
	email TEXT NOT NULL, 
	PRIMARY KEY (email), 
	UNIQUE (email)
)

CREATE TABLE recording (
	id INTEGER NOT NULL, 
	url TEXT NOT NULL, 
	owner_email TEXT, 
	public BOOLEAN, 
	pwhash TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(owner_email) REFERENCES user (email), 
	CHECK (public IN (0, 1))
)

CREATE TABLE viewer (
	id INTEGER NOT NULL, 
	viewer TEXT, 
	recording_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(viewer) REFERENCES user (email), 
	FOREIGN KEY(recording_id) REFERENCES recording (id)
)

CREATE TABLE meeting (
	id INTEGER NOT NULL, 
	host_email TEXT, 
	recording_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(host_email) REFERENCES user (email), 
	FOREIGN KEY(recording_id) REFERENCES recording (id)
)
```
