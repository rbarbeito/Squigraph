from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit
from flask_apscheduler import APScheduler
from datetime import datetime, timezone

import re

from os import path, getenv
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'LasTelarañadeCarlota!'
socketio = SocketIO(app)


file_backup = getenv('FILE_BACKUP_CHECK')

traza = {}

firts_ten = {}


@app.get("/")
def index():
    return render_template("stats.html")


@socketio.on('connect')
def test_connect():

    socketio.emit('connection', {"message": "Bienvenido al server",
                                 "topTen": firts_ten})
    print('usuario conectado: ', request.sid)


@socketio.on('message')
def handle_message(data):
    print('received message: ' + data)


def my_job(log):
    reference_time = file_control()

    with open(f'{log}', 'r', encoding='utf-8') as f:
        data = f.readline()

        while data:
            data = f.readline()

            if not data:
                break

            linea_data = re.split(
                r"(\S*)(\s{1})([0-9\s]{1,})(\s{1})(\S*)(\s{1})(\S*)(\s{1})([0-9]{1,10})(\s{1})(\S*)(\s{1})(\S*)(\s{1})(\S*)(\s{1})(\S*)(\s{1})(\S*)", data.strip())

            datos_peticion = [linea_data[i]
                              for i in range(1, len(linea_data), 2)]

            if float(reference_time) > float(datos_peticion[0]) and datos_peticion[3].split('/')[-1] == '200':
                if datos_peticion[6].split(":")[0] == 'http':
                    url = datos_peticion[6].split(":")[-1].split("/")[2]
                else:
                    url = datos_peticion[6].split(":")[0]

                if url in traza.keys():
                    traza[url] = int(traza[url]) + int(datos_peticion[4])
                else:
                    traza[url] = int(datos_peticion[4])

    temp = sorted(
        traza.items(), key=lambda item: item[1], reverse=True)[:10]

    for key, value in temp:
        firts_ten[key] = int(value)/1024**2

    socketio.emit('update_graphic',  {"topTen": firts_ten})


def file_control():
    if not path.isfile(f'{file_backup}'):
        with open(f'{file_backup}', 'w', encoding='utf-8') as f:
            f.write(str(0))

    with open(f'{file_backup}', 'r+', encoding='utf-8') as f:
        data_time = f.readline().strip()

        f.seek(0)
        f.write(str(datetime.now(timezone.utc).timestamp()))
        f.truncate()

        return data_time


if __name__ == '__main__':
    scheduler = APScheduler()
    scheduler.add_job(func=my_job, args=[
                      getenv('PATH_LOG_SQUID')], trigger='interval', id='job', seconds=10)
    scheduler.start()
    socketio.run(app, debug=True)
