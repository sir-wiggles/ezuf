FROM python:3.5-slim

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN apt-get update && apt-get install sqlite3 -y
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 80

CMD [ "gunicorn", "-b", "0.0.0.0:80", "run:app" ]
