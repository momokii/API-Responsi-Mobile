from flask import Flask, request, redirect, url_for, jsonify

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy.exc import *

from werkzeug.security import generate_password_hash, check_password_hash

from flask_cors import CORS


app = Flask(__name__)
db = SQLAlchemy(app)
CORS(app= app)
app.config['SECRET_KEY'] = 'responsimobile'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///responsi_mobile.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

import datetime


# ============================= DATABASE ============================= #

class FinishToDo:
    @staticmethod
    def get_now_time():
        return datetime.datetime.today()

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100), unique = True)
    password_hash = db.Column(db.String(500))
    nama = db.Column(db.String(100))

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, password_plain):
        self.password_hash = generate_password_hash(password_plain, salt_length=18)

    def password_checker(self, password):
        return check_password_hash(self.password_hash, password)



class Todo(db.Model):
    __tablename__ = 'todo'
    id = db.Column(db.Integer, primary_key = True)
    nama = db.Column(db.String(200))
    deskripsi = db.Column(db.String(250))
    
    
class HistoriToDo(db.Model):
    __tablename__ = 'histori_todo'
    id = db.Column(db.Integer, primary_key = True)
    nama = db.Column(db.String(200))
    deskripsi = db.Column(db.String(250))
    created_at = db.Column(db.DateTime, default = FinishToDo.get_now_time())


db.create_all()


# ============================= ======== ============================= #



@app.get('/')
def home():
    request.access_control_request_headers

    response = jsonify(Hello = "World"), 201

    response[0].headers.add_header("Allow-Control-Access-Origin", "*")
    return response

db.create_all()


@app.post('/user')
def tambah_user():
    request.access_control_request_headers

    try:
        data = request.get_json()
        username = data['username']
        nama = data['nama']
        password = data['password']

        new_user = User(
            username = username,
            password = password,
            nama = nama
        )

        db.session.add(new_user)
        db.session.commit()
        response = jsonify({
            "status" : "success",
            "msg" : f"tambah akun username : {username}"
        }), 201

    except:
        response = jsonify({
            "status" : "error",
            "msg" : f"gagal tambah akun"
        }), 400

    response[0].headers.add_header("Allow-Control-Access-Origin", "*")
    return response




@app.post('/user/login')
def login():
    request.access_control_request_headers

    try:
        data = request.get_json()
        username = data['username']
        password = data['password']

        user = User.query.filter_by(username = username).first()
        if user:
            if user.password_checker(password):
                response = jsonify({
                    "success" : {
                        "nama" : user.nama,
                        "username": username,
                        "token" : str(user.password_hash)
                    }
                }), 200

            else:
                response = jsonify({
                    "status": "error",
                    "msg": f"pass salah"
                }), 400

        else:
            response = jsonify({
                "status": "error",
                "msg": f"akun tak ada"
            }), 400

    except:
        response = jsonify({
            "status": "error",
            "msg": f"gagal login"
        }), 400


    response[0].headers.add_header("Allow-Control-Access-Origin", "*")
    return response





# ------------- TODO-----------------
@app.get('/todo/<int:id>')
@app.get('/todo')
def get_todo(id = None):
    request.access_control_request_headers

    if id != None:
        todo = Todo.query.get(id)
        response = jsonify({
            "status" : "success",
            "data" : {
                "nama" : todo.nama,
                "deskripsi" : todo.deskripsi,
                "id" : todo.id
            }
        }), 200

    else:
        todo = Todo.query.all()
        todo_list = []
        for data in todo:
            datatodo = {
                "nama" : data.nama,
                "deskripsi" : data.deskripsi,
                "id" : data.id
            }
            todo_list.append(datatodo)

        response = jsonify({
            "status" : "success",
            "data" : todo_list
        }), 200



    response[0].headers.add_header("Allow-Control-Access-Origin", "*")
    return response




@app.post('/todo')
def tambah_todo():
    request.access_control_request_headers

    try:
        data = request.get_json()
        nama = data['nama_todo']
        deskripsi = data['deskripsi_todo']

        new_todo = Todo(
            nama = nama,
            deskripsi = deskripsi
        )
        db.session.add(new_todo)
        db.session.commit()
        response = jsonify({
            "status": "success",
            "msg": f"berhasil tambah todo {new_todo}"
        }), 200


    except:
        response = jsonify({
            "status": "error",
            "msg": f"gagal tambah todo"
        }), 400


    response[0].headers.add_header("Allow-Control-Access-Origin", "*")
    return response




@app.put('/todo')
@app.patch('/todo')
def edit_todo():
    request.access_control_request_headers

    data = request.get_json()
    todo_edit = Todo.query.get(data['id'])

    todo_edit.nama = data['nama_baru']
    todo_edit.deskripsi = data['deskripsi_baru']

    db.session.commit()
    response = jsonify({
        "status" : "success",
        "msg" : f"Berhasil edit todo dengan id {data['id']}"
    }), 200

    response[0].headers.add_header("Allow-Control-Access-Origin", "*")
    return response



@app.delete('/todo')
def hapus_todo():
    request.access_control_request_headers

    id = int(request.get_json()['id'])
    todo = Todo.query.get(id)
    db.session.delete(todo)
    db.session.commit()

    response = jsonify({
        "status" : "success",
        "msg" : f"berhasil hapus todo dengan id : {id}"
    }), 200


    response[0].headers.add_header('Allow-Control-Access-Origin', '*')
    return response

# ------------- TODO SELESAI -----------------
@app.post('/selesai')
def selesai():
    request.access_control_request_headers

    todo_selesai = Todo.query.get(request.get_json()['id'])

    new_history = HistoriToDo(
        nama = todo_selesai.nama,
        deskripsi = todo_selesai.deskripsi
    )
    db.session.add(new_history)
    db.session.delete(todo_selesai)
    db.session.commit()

    response = jsonify({
        'status' : 'success',
        'msg' : 'berhasil menyelesaikan todo'
    }), 200

    response[0].headers.add_header('Allow-Control-Access-Origin', '*')
    return response


@app.get('/todo/histori')
def get_todo_histori():
    request.access_control_request_headers

    todo = HistoriToDo.query.all()
    todo_list = []
    for data in todo:
        datatodo = {
            "nama" : data.nama,
            "deskripsi" : data.deskripsi,
            "id" : data.id,
            "tgl_selesai" : data.created_at
        }
        todo_list.append(datatodo)

    response = jsonify({
        "status" : "success",
        "data" : todo_list
    }), 200

    response[0].headers.add_header("Allow-Control-Access-Origin", "*")
    return response




if __name__ == "__main__":
    app.run(debug= True, port= 8200)