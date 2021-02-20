from flask import Flask,request
import database
from Helper import Node, Message, Queue
app = Flask(__name__)

queue = {}

@app.route("/")
def home():
    return "<h1>Running</h1>"
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
    channel_id = request.form.get("channel_id")
    if channel_id is not None and user_id is not None and msg_text is not None:
        msg, u_two = database.add_msg(channel_id, int(user_id), msg_text)
        if msg is not None:
            uni = str(channel_id)+str(u_two) 
            q = queue.get(uni)
            if q is not None:
                q.insert(Node(msg))
            else:
                queue[uni] = Queue()
                queue[uni].insert(Node(msg))
            return {"status":0,"msg":"msg has been added"}
        return {"status":1,"msg":"channel Id invlid "}
    return {"status":1,"msg":"userId and text should not be null"}

@app.route("/msg/all")
def all_msg():
    user_id = request.args.get("user_id")
    channel_id = request.args.get("channel_id")
    if user_id is not None and channel_id is not None:
        messages = database.read_all_msg(user_id,channel_id)
        if messages is not None:
            d = {"status":0,"data":[]}
            for i in messages:
                d["data"].append({"msg_id":i[0],"channel_id":i[1],"user_id":i[2],"msg":i[3],"chain_val":float(i[4]),"sent_at":i[5]})
            return d
        return {"status":1,"msg":"invalid userId and channelId"}
    return {"status":1,"msg":"userId and channelId is null"}
if __name__ == "__main__":
    app.run(port=3000,debug=True)