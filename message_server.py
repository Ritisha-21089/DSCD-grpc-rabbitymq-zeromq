# groups register, user requests group list

import zmq
import json

MAXGROUPS = 10
GROUPS = {}


def Serve(port):
    context = zmq.Context()
    repsocket = context.socket(zmq.REP)
    repsocket.bind(f'tcp://192.168.44.146:{port}')

    print(f"Server started, listening on {port}")
    while True:
        # wait for request from client
        message = repsocket.recv_string()
        msgStr = json.loads(message)
        
        res = ParseMessage(msgStr)
        res1 = json.dumps(res)
        repsocket.send_string(res1)


def RegisterGroup(request):
    global GROUPS
    print(f'JOIN REQUEST FROM {request["groupname"]} - {request["ip"]}:{request["port"]}')
    try:
        if len(GROUPS) >= MAXGROUPS:
            raise Exception("Capacity reached. No more groups can be added")

        server_string = f"{request['groupname']} - {request['ip']}:{request['port']}"
        if server_string in GROUPS:
            raise Exception("Duplicate request")

        GROUPS[server_string] = True
        # print("y")
        y= {"status": "SUCCESS"}
        # print("Status: ", y["status"])
        return y
    except:
        # print("n")
        n = {"status": "FAIL"}
        # print("Status: ", n["status"])
        return n


def GetGroupList(request):
    group_list = []
    print(f'GROUP LIST REQUEST FROM {request["id"]}')
    try:
        for key, value in GROUPS.items():
            if value:
                group_list.append(key)
        p = {"status": "SUCCESS", "groups": group_list}
        return p
    except:
        l = {"status": "FAIL"}
        return l


def ParseMessage(message):  # message is a python dict
    # res = json.dumps({"status": "FAIL"})
    sel = message["method"]
    if sel.lower() == "registergroup":
        res = RegisterGroup(message["args"])
    elif sel.lower() == "getgrouplist":
        res = GetGroupList(message["args"])
    return res


if __name__ == '__main__':
    port = 5555
    try:
        Serve(port)
    except:
        print("Could not bind server to a port")
        exit(1)
