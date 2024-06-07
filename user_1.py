# request message_server for group list, join group request, leave group request, 
# send message, get message request

import zmq
import json
import uuid

USER_UUID = str(uuid.uuid1())
JOINED_GROUPS = {}

class UserSocket:
    def __init__(self, server_address):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.server_address = server_address

    def connect_u(self):
        self.socket.connect(self.server_address)

    def disconnect_u(self):
        self.socket.disconnect(self.server_address)

    def send_json_u(self, message):
        msgStr = json.dumps(message)
        self.socket.send_string(msgStr)

    def recv_json_u(self):
        response = self.socket.recv_string()
        return json.loads(response)

    def GetGroupList(self):
        # print(f'GROUP LIST REQUEST FROM {USER_UUID}')
        message = {"method": "GetGroupList", "args": {"id": USER_UUID}}
        self.send_json_u(message)
        response = self.recv_json_u()
        # print(response)
        if response["status"].lower() == "success":
            print("Group List [NAME - IP:PORT]:")
            for server in response["groups"]:
                print(server)
                # print(f"  {server['groupname']} - {server['ip']}")
        else:
            print("Failed to get group list.")
            
    def JoinGroup(self, group_port):
        # print(f'JOIN REQUEST FROM {USER_UUID} for group port: {group_port}')
        message = {"method": "JoinGroup", "args": {"id": USER_UUID}}
        
        # Create a new REQ socket for joining the group
        join_socket = self.context.socket(zmq.REQ)
        join_socket.connect(f'tcp://192.168.44.146:{group_port}')
        msgStr = json.dumps(message)
        join_socket.send_string(msgStr)
        
        # Receive the response and process it
        res = join_socket.recv_string()
        response = json.loads(res)
        
        # Closing the socket after joining
        join_socket.close()
        
        if response["status"].lower() == "success":
            print(f"Joined the group {response['group_name']}.")
            print(response["status"])
            JOINED_GROUPS[group_port] = response["group_name"]
        else:
            print(f"Failed to join the group: {response['error']}")
    
    def LeaveGroup(self, group_port):
        # print(f'LEAVE REQUEST FROM {USER_UUID} with PORT: {group_port}')
        message = {"method": "LeaveGroup", "args": {"id": USER_UUID, "group_port": group_port}}
        
        leave_socket = self.context.socket(zmq.REQ)
        leave_socket.connect(f'tcp://192.168.44.146:{group_port}')
        msgStr = json.dumps(message)
        leave_socket.send_string(msgStr)
        
        res = leave_socket.recv_string()
        response = json.loads(res)
        
        # Closing the socket after joining
        leave_socket.close()
        
        if response["status"].lower() == "success":
            print(f"Left the group {response['group_name']}.")
            print(response["status"])
            JOINED_GROUPS.pop(group_port, None)
        else:
            print(f"Failed to leave the group: {response['error']}")
    
    def GetMessage(self, group_port, timestamp=None):
        # print(f'MESSAGE REQUEST FROM {USER_UUID} [{group_port}]')
        message = {
            "method": "GetMessage",
            "args": {"id": USER_UUID, "group_port": group_port, "timestamp": timestamp}
        }
        
        get_msg_socket = self.context.socket(zmq.REQ)
        get_msg_socket.connect(f'tcp://192.168.44.146:{group_port}')
        msgStr = json.dumps(message)
        get_msg_socket.send_string(msgStr)
        
        res = get_msg_socket.recv_string()
        response = json.loads(res)
        
        # Close the socket after joining
        get_msg_socket.close()
        if response["status"].lower() == "success":
            print("Messages:")
            for msg in response["messages"]:
                # print(f"  {msg['author']} - {msg['content']} ({msg['timestamp']})")
                print(f" ({msg['timestamp']})  {msg['content']}")
        else:
            print("Failed to get messages.")

    def SendMessage(self, group_port, content):
        # print(f'MESSAGE SEND FROM {USER_UUID}')
        message = {
            "method": "SendMessage",
            "args": {"id": USER_UUID, "group_port": group_port, "content": content}
        }
        
        send_socket = self.context.socket(zmq.REQ)
        send_socket.connect(f'tcp://192.168.44.146:{group_port}')
        msgStr = json.dumps(message)
        send_socket.send_string(msgStr)
        
        res = send_socket.recv_string()
        response = json.loads(res)
        
        # Close the socket after joining
        send_socket.close()
        print(response["status"])

if __name__ == '__main__':
    server_address = "tcp://192.168.44.146:5555"  # Replace with the actual address of the message server
    user_socket = UserSocket(server_address)
    user_socket.connect_u()

    while True:
        try:
            print("\n---- Operations ----\n")
            print("1: Get Group List")
            print("2: Join Group")
            print("3: Leave Group")
            print("4: Get Messages")
            print("5: Send Message")
            print("6: Exit")

            choice = int(input("Enter your choice: "))

            if choice == 1:
                user_socket.GetGroupList()

            elif choice == 2:
                group_port = input("Enter the group PORT to join: ")
                user_socket.JoinGroup(group_port)

            elif choice == 3:
                group_port = input("Enter the group PORT to leave: ")
                user_socket.LeaveGroup(group_port)

            elif choice == 4:
                group_port = input("Enter the group PORT to get messages: ")
                timestamp = input("Enter timestamp [DD/MM/YYYY HH:MM:SS] (press Enter to skip): ")
                user_socket.GetMessage(group_port, timestamp)

            elif choice == 5:
                group_port = input("Enter the group PORT to send message: ")
                content = input("Enter the message content: ")
                user_socket.SendMessage(group_port, content)

            elif choice == 6:
                user_socket.disconnect_u()
                exit(0)

        except KeyboardInterrupt:
            user_socket.disconnect_u()
            exit(0)
        except Exception as e:
            print(f"Error: {e}")