class Message:
    def __init__(self, msg_id, channel_id, user_name, msg, chain_val, time):
        self.msg_id = msg_id
        self.channel_id = channel_id
        self.user_name = user_name
        self.msg = msg
        self.chain_val = chain_val
        self.time = time

class Node:
    def __init__(self,val, extra=None):
        self.val = val
        self.prev = None
        self.next = None
        self.extra = extra

class Queue:
    def __init__(self):
        self.length = 0
        self.root = None
        self.tail = None
    
    def insert(self,node: Node):
        if self.root == None:
            self.root = node
            self.tail = node
        else:
            self.tail.next = node
            node.prev = self.tail
            self.tail = node
        self.length += 1

    def insert_top(self, node: Node):
        if self.root == None:
            self.root = node
            self.tail = node
        else:
            node.next = self.root
            self.root.prev  = node
            self.root = node 
        self.length += 1

    def pop(self) -> Node:
        head = self.root
        if self.root is not None and self.root.next is not None:
            self.root.next.prev = None
            self.root = self.root.next
            head.next = None
            self.length -= 1
        elif self.root is not None:
            self.tail = self.root = None 
            self.length -= 1
        return head

    def pop_end(self):
        end = self.tail
        if self.tail is not None and end.prev is not None:
            self.tail.prev.next = None
            self.tail = self.tail.prev
            end.prev = None
        else:
            self.head = self.tail = None
        self.length -= 1
        return end

class LRU_CACHE:
    def __init__(self, callback, capacity=10):
        self.callback = callback
        self.capacity = capacity
        self.cache = Queue()
        self.hash_map = {}

    def put(self, key, val):      
        node = Node(val, key)
        self.hash_map[key] = node
        if self.cache.length == self.capacity:
            end = self.cache.pop_end()
            self.callback.update(end.extra, end.val)
            del self.hash_map[end.extra]
        self.cache.insert_top(node)

    def update_value(self,key,value):
        node = self.hash_map.get(key)
        if node is not None:
            node.val = value
            
    def get(self, key):
        node = self.hash_map.get(key)
        if node is not None and node != self.cache.root:
            if node.next is not None:
                node.next.prev = node.prev
            if node.prev is not None: 
                node.prev.next = node.next
                if node == self.cache.tail:
                    self.cache.tail = node.prev    
            node.next = None
            node.prev = None
            self.cache.root.prev = node
            node.next = self.cache.root 
            self.cache.root = node
        return node.val if node != None else None



