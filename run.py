from fuze import app, db
from fuze.app import configure

app = configure(app, db)

if __name__ == "__main__":
    app.run()
