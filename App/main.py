from flask import Flask,request
import database
from Helper import Node, Message
app = Flask(__name__)

queue = {}


@app.route("/login",methods=["POST"])    
def login():
    if request.method == "POST":
        user_name = request.form.get("user_name")
        password = request.form.get("password")
        if user_name is not None and password is not None:
            return database.login(user_name,password)
        return {"status":1,"msg":"user name and password is null"}

@app.route("/signup",methods=["POST"])    
def signup():
    if request.method == "POST":
        user_name = request.form.get("user_name")
        password = request.form.get("password")
        if user_name is not None and password is not None:
            return database.signup(user_name,password)
        return {"status":1,"msg":"username and password is null"}

@app.route("/user/delete",methods=["POST"])
def delete_user(id):
    id = request.args.get("id")
    if id is not None:
        return database.delete_user(id)
    return {"status":1,"msg":" id is null"}

@app.route("/msg/add",methods=["POST"])
def add_msg():
    user_id = request.form.get("user_id")
    msg_text = request.form.get("text")
    channel_id = request.args.get("channel_id")
    if channel_id is not None and user_id is not None and msg_text is not None:
        pass
    return {"status":1,"msg":"userId and text should not be null"}

if __name__ == "__main__":
    app.run(port=3000,debug=True)