# register group, retrieves messages of the group, receives message from user, 
# user can join and leave

from datetime import datetime
import zmq
import json

class GroupServer:
    def __init__(self):
        # self.UUID = str(uuid.uuid1())
        self.NAME = "hi"
        self.GROUP_IP = "192.168.44.146"
        # self.GROUP_PORT = 5000  # Replace with the actual port number

        self.MAX_USERS = 10
        self.USERTELE = []
        self.MESSAGES = []

        self.context = zmq.Context()
        self.repsocket = self.context.socket(zmq.REP)
        self.reqsocket = self.context.socket(zmq.REQ)
        self.port = None

    def RegisterGroup(self):
        try:
            print("Attempting to register the group...")
            self.NAME = input("Enter group name: ")
            args = {"groupname": self.NAME, "ip": self.GROUP_IP, "port": self.port}
            message = {"method": "RegisterGroup", "args": args}

            msgStr = json.dumps(message)
            self.reqsocket.send_string(msgStr)
            res = self.reqsocket.recv_string()
            ser = json.loads(res)
           
            print(f"{ser['status']}")

            return ser
        except Exception as e:
            print(f"Error in RegisterGroup: {e}")
            return {"status": "FAIL"}
    
    def JoinGroup(self, request):
        try:
            user_id = request["id"]
            print(f'JOIN REQUEST FROM {user_id}')

            if len(self.USERTELE) < self.MAX_USERS and user_id not in self.USERTELE:
                self.USERTELE.append(user_id)
                response = {"status": "SUCCESS", "group_name": self.NAME}
            else:
                response = {"status": "FAIL", "error": "Group is full or user already in the group"}

            return json.dumps(response)
        except Exception as e:
            print(f"Error in JoinGroup: {e}")
            return json.dumps({"status": "FAIL", "error": str(e)})

  
    def LeaveGroup(self, request):
        # print(self.USERTELE)
        try:
            user_id = request["id"]
            print(f'LEAVE REQUEST FROM {user_id} ')
            
            if user_id in self.USERTELE:        
                self.USERTELE.remove(user_id)
                response = {"status": "SUCCESS", "group_name": self.NAME}
            else: 
                response = {"status": "FAIL", "error": "User is not a member of the group."}
            return json.dumps(response)
        except Exception as e:
            print(f"Error in LeaveGroup: {e}")
            return json.dumps({"status": "FAIL", "error": str(e)})
    
    def GetMessage(self, request):
        try:
            # print("Received Request in GetMessage:", request)
            print(f'MESSAGE REQUEST FROM {request["id"]}')
            if not isinstance(request, dict):
                print("Invalid request format. Expected a dictionary.")
                return json.dumps({"status": "FAIL"})

            user_id = request.get("id", None)
            timestamp = request.get("timestamp", None)

            if user_id not in self.USERTELE:
                print(f"User {user_id} is not part of the group.")
                return json.dumps({"status": "FAIL", "error": "User is not part of the group"})

            res_messages = []

            for message in self.MESSAGES:
                if timestamp:
                    if datetime.strptime(message["timestamp"], "%d/%m/%Y %H:%M:%S") >= datetime.strptime(timestamp, "%d/%m/%Y %H:%M:%S"):
                        res_messages.append({"content": message["content"], "timestamp": message["timestamp"]})
                else:
                    res_messages.append({"content": message["content"], "timestamp": message["timestamp"]})

            return json.dumps({"status": "SUCCESS", "messages": res_messages})
        except Exception as e:
            print("Error in GetMessage:", e)
            return json.dumps({"status": "FAIL"})


    def SendMessage(self, request):
        print(f'MESSAGE SEND FROM {request["id"]}')
        try:
            if not request["id"] in self.USERTELE:
                raise Exception("User is not part of the group")

            current_time = datetime.now()

            new_message = {
                "content": request["content"],
                "author": request["id"],
                "timestamp": current_time.strftime("%d/%m/%Y %H:%M:%S")
            }
            # print(new_message)

            self.MESSAGES.append(new_message)
            return json.dumps({"status": "SUCCESS"})
        except Exception as e:
            print(f"Error in SendMessage: {e}")
            return json.dumps({"status": "FAIL"})

    def Serve(self):
        try:
            self.port = self.repsocket.bind_to_random_port(
                'tcp://192.168.44.146', min_port=5600, max_port=6004, max_tries=100)
        except Exception as e:
            print(f"Could not bind group server to a port: {e}")
            self.repsocket.close()
            self.reqsocket.close()
            exit(1)

        try:
            self.reqsocket.connect("tcp://192.168.44.146:5555")
            ans = self.RegisterGroup()

            if not (ans["status"].lower() == "success"):
                print("Could not register the group. Exiting.")
                exit(1)
        except Exception as e:
            print(f"Error in Serve: {e}")
            exit(1)
        finally:
            self.reqsocket.close()

        print(f"Group server started, listening on {self.port}")
        try:
            while True:
                # wait for request from client
                message = self.repsocket.recv()
                res = self.ParseMessage(message=json.loads(message)).encode('UTF-8')
                self.repsocket.send(res)
        except KeyboardInterrupt:
            print("Server stopped.")
        except Exception as e:
            print(f"Error in Serve loop: {e}")
        finally:
            self.repsocket.close()

    def ParseMessage(self, message):
        try:
            # print("Received Message:", message)

            # Check if the message is a dictionary
            if not isinstance(message, dict):
                print("Invalid message format. Expected a dictionary.")
                return json.dumps({"status": "FAIL"})

            # Check if "method" key is present in the dictionary
            if "method" not in message:
                print("Method key not found in the message.")
                return json.dumps({"status": "FAIL"})

            method_lower = str(message.get("method")).lower()

            if method_lower == "joingroup":
                res = self.JoinGroup(message.get("args", {}))
            elif method_lower == "leavegroup":
                res = self.LeaveGroup(message.get("args", {}))
            elif method_lower == "getmessage":
                res = self.GetMessage(message.get("args", {}))
            elif method_lower == "sendmessage":
                res = self.SendMessage(message.get("args", {}))
            else:
                res = json.dumps({"status": "FAIL", "error": "Unknown method"})

            return res
        except Exception as e:
            print(f"Error in ParseMessage: {e}")
            return json.dumps({"status": "FAIL"})

if __name__ == '__main__':
    group_server = GroupServer()
    group_server.Serve()