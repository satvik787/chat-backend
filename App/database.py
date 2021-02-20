import mysql.connector
from datetime import datetime
from Helper import Node, Message, LRU_CACHE
from math import floor
from concurrent.futures import ThreadPoolExecutor

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="pothukuchi",
    auth_plugin='mysql_native_password',
    database="chat")

cursor = mydb.cursor()
executor = ThreadPoolExecutor(2)

class Callback:
    def update(self,user_id, msg_count):
        self.db_msg_count(user_id, msg_count)
    def db_msg_count(self,user_id, msg_count):
        cursor.execute("UPDATE users SET msg_count = %s WHERE user_id = %s",(msg_count, user_id))

active_users = LRU_CACHE(Callback(),capacity=1)

def login(user_name,password) -> dict:
    cursor.execute("SELECT * FROM users WHERE user_name = %s",(user_name,))
    user_data = cursor.fetchall()
    if len(user_data) > 0:
        user_id, user_name, image_path, p = user_data[0]
        # TODO add profile path
        if password == p:
            return {"status":0, "id":user_id, "user_name":user_name, "user_profile":image_path}
        return {"staus":1,"msg":"incorrect Password"}
    return {"status":1,"msg":"Username does not exist"}

def signup(user_name, password) -> dict:
    cursor.execute("SELECT * FROM users WHERE user_name = %s",(user_name,))
    user_data = cursor.fetchall()
    if len(user_data) == 0:
        query = "INSERT INTO users (user_name,password) values (%s,%s)"
        cursor.execute(query,(user_name,password))
        mydb.commit()
        return login(user_name,password)
    return {"status":1,"msg":"username {} already exists".format(user_name)}

def delete_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id = %s",(user_id,))
    user_data = cursor.fetchall()
    if len(user_data) > 0:
        cursor.execute("DELETE FROM users WHERE user_id = %s",(user_id,))
        mydb.commit()
        return {"status":0}
    return {"status":1,"msg":"UserID does not exist"}

def add_msg(channel_id, user_id, text):
    cursor.execute("SELECT * FROM channels WHERE channel_id = %s and user_one_id = %s or user_two_id = %s",(channel_id,user_id,user_id))
    channel = cursor.fetchall()
    if len(channel) > 0:
        chain_val,u_two = gen_chain_val(channel, user_id) # chain val, other user id
        date_time = datetime.now()
        now = date_time.strftime("%d/%m/%y %H:%M")
        msg_id = active_users.get(user_id)
        if msg_id == None:
            msg_count = get_user(user_id)[3]  # retrieving msg_count from database
            if msg_count == None:
                msg_id = user_id * 1000
            elif msg_count + 1 == ((msg_count // 1000) + 1) * 1000:
                u_id = (msg_count // 1000)
                cursor.execute("DELETE FROM messages WHERE user_id = %s",(u_id,))
                msg_id =  u_id * 1000
            else:
                msg_id = msg_count + 1
            active_users.put(user_id,msg_id) # adding user to cache
        else:
            if msg_id + 1 == ((msg_id // 1000) + 1) * 1000:
                u_id = (msg_count // 1000)
                cursor.execute("DELETE FROM messages WHERE user_id = %s",(u_id,))
                msg_id =  u_id * 1000
            else:
                msg_id += 1
            active_users.update_value(user_id,msg_id)
        cursor.execute("UPDATE users SET msg_count = %s WHERE user_id = %s",(msg_id,user_id))
        db_add_msg(msg_id, channel_id, user_id, text, chain_val, now)
        return Message(msg_id,channel_id,user_id,text,chain_val,now), u_two 
    return None, None

def db_add_msg(msg_id, channel_id, user_id, text, chain_val,sent_at):
    query = "INSERT INTO messages (msg_id,channel_id,user_id,msg,chain_val,sent_at) values(%s,%s,%s,%s,%s,%s)"
    cursor.execute(query,(msg_id,channel_id,user_id,text,chain_val,sent_at))
    mydb.commit()

def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id = %s",(user_id,))
    user = cursor.fetchall()
    return user[0] if len(user) > 0 else None 


def gen_chain_val(channel, user_id):
    chain_val,u_two = 0, None
    if channel[0][1] == user_id:
        sub, obj = float(channel[0][3]), float(channel[0][4])
        if sub == 0 and obj == 0:
            chain_val = 1.0
        elif sub > obj:
            chain_val = sub + 0.1
        elif sub < obj:
            chain_val = floor(obj) + 1.0
        u_two = channel[0][2]
        cursor.execute("UPDATE channels SET chain_one = %s",(chain_val,))
    elif channel[0][2] == user_id:
        sub, obj = float(channel[0][4]), float(channel[0][3])
        if sub == 0 and obj == 0:
            chain_val = 1.0
        elif sub > obj:
            chain_val = sub + 0.1
        elif sub < obj:
            chain_val = floor(obj) + 1.0
        u_two = channel[0][1]
        executor.submit(cursor.execute,"UPDATE channels SET chain_two = %s",(chain_val,)) 
    return chain_val,u_two

def read_all_msg(user_id,channel_id):
    cursor.execute("SELECT * FROM messages WHERE user_id = %s and channel_id = %s",(user_id,channel_id))
    msg = cursor.fetchall()
    return msg if len(msg) > 0 else None 