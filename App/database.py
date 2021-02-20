import mysql.connector
from uuid import uuid4
from datetime import datetime
from Helper import Node, Message, LRU_CACHE
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
        executor.submit(db_add_msg,user_id, msg_count)
    def db_msg_count(self,user_id, msg_count):
        cursor.execute("UPDATE users SET msg_count = %s WHERE user_id = %s",(msg_count, user_id))

active_users = LRU_CACHE(Callback())

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
        chain_val = 0
        if channel[0][1] == user_id:
            sub, obj = channel[0][3], channel[0][4]
            if sub > obj:
                chain_val = sub
            elif sub < obj:
                chain_val = obj + 1
        elif channel[0][2] == user_id:
            sub, obj = channel[0][4], channel[0][3]
            if sub > obj:
                chain_val = sub
            elif sub < obj:
                chain_val = obj + 1
        date_time = datetime.now()
        now = date_time.strftime("%d/%m/%y %H:%M")
        msg_id = active_users.get(user_id)
        if msg_id == None:
            msg_count = get_user(user_id)[3]
            if msg_count == None:
                msg_id = user_id * 1000
            else:
                msg_id = msg_count + 1
            active_users.put(user_id,msg_id)
        executor.submit(db_add_msg,msg_id, channel_id, user_id, text, chain_val, now)
        return Message(msg_id,channel_id,user_id,text,chain_val,now) 
    return None

def db_add_msg(msg_id, channel_id, user_id, text, chain_val,sent_at):
    query = "INSERT INTO messages (msg_id,channel_id,user_id,msg,chain_val,sent_at) values(%s,%s,%s,%s,%s,%s)"
    cursor.execute(query,(msg_id,channel_id,user_id,text,chain_val,sent_at))
    cursor.commit()

def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id = %s",(user_id,))
    user = cursor.fetchall()
    return user[0] if user > 0 else None 


