from flask import Flask,request
import database
from Helper import Node, Queue
app = Flask(__name__)

queue = {}

def jsonify_msg(messages):
    if messages is not None:
        d = {"status":0,"data":[]}
        for i in messages:
            d["data"].append({"msg_id":i[0],"channel_id":i[1],"user_id":i[2],"msg":i[3],"chain_val":float(i[4]),"sent_at":i[5]})
        return d
    return {"status":1,"msg":"Invalid ChannelID"}


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

try:
    @app.route("/msg/new",methods=["POST"])
    def add_msg():
        user_id = request.form.get("user_id")
        msg_text = request.form.get("text")
        channel_id = request.form.get("channel_id")
        if channel_id is not None and user_id is not None and msg_text is not None:
            msg, u_two = database.add_msg(channel_id, int(user_id), msg_text)
            if msg is not None and u_two is not None:
                uni = str(channel_id)+str(u_two) 
                q = queue.get(uni)
                if q is not None:
                    q.insert(Node(msg))
                return {"status":0,"msg":"msg has been added"}
            return {"status":1,"msg":"channel Id invlid "}
        return {"status":1,"msg":"userId and text should not be null"}
except Exception as e:
    database.save_msg_count()
    print(e.__class__)
    print("Cause",e.__cause__)

@app.route("/msg/all")
def all_msg():
    user_id = request.args.get("user_id")
    channel_id = request.args.get("channel_id")
    if user_id is not None and channel_id is not None:
        messages = database.read_all_msg(channel_id)
        queue[str(channel_id)+str(user_id)] = Queue()
        return jsonify_msg(messages)
    return {"status":1,"msg":"userId and channelId is null"}

@app.route("/msg/new")
def get_new_msg():
    user_id = request.args.get("user_id")
    channel_id = request.args.get("channel_id")
    if user_id is not None and channel_id is not None:
        q = queue.get(str(channel_id) + str(user_id))
        if q is not None:
            messages, trav = {"status":0,"data":[]}, q.pop()
            while trav != None:
                i = trav.val
                messages["data"].append({"msg_id":i[0],"channel_id":i[1],"user_id":i[2],"msg":i[3],"chain_val":float(i[4]),"sent_at":i[5]})
                trav = q.pop()
            return messages
        return {"status":1,"msg":"user not present in queue"}
    return {"status":1,"msg":"userID and ChannelID is null"}

@app.route("/user/search")
def search():
    user_name = request.args.get("user_name")
    if user_name is not None:
        return {"status":0,"data":database.search_user(user_name)}
    return {"status":1,"msg":"userID and ChannelID is null"}

@app.route("/user/exit")
def user_exit():
    user_id = request.args.get("user_id")
    if user_id is not None: 
        database.active_users.remove(user_id)
        return {"status":0,"msg":"user_exit"}
    return {"status":1,"msg":"userID is null"}

@app.route("/channel/new")
def channel_new():
    user_one = request.args.get("user_one")
    user_two = request.args.get("user_two")
    if user_one is not None and user_two is not None:
        if user_one != user_two:
            channel = database.channel_exists(user_one,user_two)
            if channel is None:
                channel = database.create_channel(user_one,user_two)
            return {"status":0,"data":{"channel_id":channel[0],"user_one":channel[1],"user_two":channel[2],"chain_one":float(channel[3]),"chain_two":float(channel[4])}}
        return {"status":1,"msg":"invalid id"}
    return {"status":1,"msg":"userID is null"}

@app.route("/channel/all")
def channel_all():
    user_id = request.args.get("user_id")
    if user_id is not None:
        channels = database.channel_all(user_id)
        d = {"status":0,"data":[]}
        for i in channels:
            d["data"].append({"channel_id":i[0],"user_one":i[1],"user_two":i[2],"chain_one":float(i[3]),"chain_two":float(i[4])})
        return d
    return {"status":1,"msg":"userID is null"}



@app.route("/channel/exit")
def channel_exit():
    user_id = request.args.get("user_id")
    channel_id = request.args.get("channel_id")
    if user_id is not None and channel_id is not None:
        uni = str(channel_id)+str(user_id)
        if queue.get(uni) is not None:
            del queue[uni]
            return {"status":0,"msg":"removed from queue"}
        return {"status":1,"msg":"user not presnet in queue"}
    return {"status":1,"msg":"userID and ChannelID is null"}


if __name__ == "__main__":
    app.run(port=3000,debug=True) 