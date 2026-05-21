# VDBL console

import sys
import json
import time
import requests
import traceback


def try_get_cmd(url : str, req_id : str):
    r = requests.get( url + "/" + req_id)
    r.raise_for_status()
    for line in r.iter_lines():
        if line:
            data = json.loads(line.decode( "utf-8" ))
            return data[ "data" ]
    return ""

def get_cmd(url : str, req_id : str):
    for i in range(1, 100):
        time.sleep(0.1)
        ret = try_get_cmd(url, req_id)
        if len(ret) > 0:
            return ret
    return ""

def post_cmd(url : str, hdr : dict, cmd : str):
    req_id = ""
    payload = {
        "statement": cmd,
        "timeout": 10,
    }
    r = requests.post( url, headers= hdr, data=json.dumps(payload) )
    r.raise_for_status()
    for line in r.iter_lines():
        if line:
            data = json.loads(line.decode("utf-8"))
            return data["data"]["id"]
    return req_id

def exec_cmd( url : str, hdr : str, cmd : str ):
    req_id = post_cmd(url, hdr, cmd)
    res = get_cmd( url, req_id )
    return res

if __name__ == "__main__":
    # Simple VDBL console
    VDB_HEADER = { "Content-Type" : "application/json" }
    VDB_URL = "http://localhost:8081/api/v1"
    if len( sys.argv ) > 1:
        VDB_URL = sys.argv[ 1 ]
    print("Connect to vdbl url: " + VDB_URL)
    while True:
        try:
            cmd = input("vdbl> ").strip()
            if not cmd:
                continue
            if cmd.lower() in {"quit", "exit", "q", "e"}:
                break
            result = exec_cmd( VDB_URL, VDB_HEADER, cmd )
            print("vdbl: " + str(result))
        except Exception as e:
            #print(f"vdbl exception: {e}")
            pass
            
