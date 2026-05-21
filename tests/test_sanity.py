# VDBL Sanity tests

import json
import time
import requests
import traceback

def try_get_cmd(url : str, req_id : str):
    r = requests.get( url + "/" + req_id)
    r.raise_for_status()
    for line in r.iter_lines():
        if line:
            data = json.loads(line.decode("utf-8"))
            return data["data"]
    return ""

def get_cmd(url : str, req_id : str):
    for i in range(1, 100):
        time.sleep(0.01)
        ret = try_get_cmd(url, req_id)
        if len(ret) > 0:
            return ret
    return ""

def get_info(url : str):
    r = requests.get( url )
    r.raise_for_status()
    for line in r.iter_lines():
        if line:
            data = json.loads(line.decode("utf-8"))
            return( data )
    return ""
            
def get_info_done(url : str):
    r = requests.get( url )
    r.raise_for_status()
    for line in r.iter_lines():
        if line:
            data = json.loads(line.decode("utf-8"))
            return int(data["done"])
    return 0
    
def get_info_waiting(url : str):
    r = requests.get( url )
    r.raise_for_status()
    for line in r.iter_lines():
        if line:
            data = json.loads(line.decode("utf-8"))
            return int(data["waiting"])
    return 0

def post_cmd(url : str, hdr : dict, cmd : str):
    req_id = ""
    payload = { "statement": cmd }
    r = requests.post( url, headers= hdr, data=json.dumps(payload) )
    r.raise_for_status()
    for line in r.iter_lines():
        if line:
            data = json.loads(line.decode("utf-8"))
            return data["data"]["id"]
    return req_id

def exec_cmd( url : str, hdr : str, cmd : str ):
    req_id = post_cmd(url, hdr, cmd)
    print("send cmd: " + cmd + " ... ")
    res = get_cmd( url, req_id )
    assert len(res) > 0
    print("result: " + str(res))
    assert "result" in res
    assert "status" in res["result"]
    assert "ok" == res["result"]["status"]

def exec_cmds(url : str, url_batch : str, hdr : dict, cmds ):
    payload = { "statements": cmds }
    r = requests.post( url_batch, headers= hdr, data=json.dumps(payload) )
    r.raise_for_status()
    print("send cmds: " + str(cmds) + " ... ")
    req_ids = []
    for line in r.iter_lines():
        if line:
            data = json.loads(line.decode("utf-8"))
            req_ids = data["data"]["ids"]
            break
    for req_id in req_ids:
        res = get_cmd( url, req_id )
        assert len(res) > 0
        print("result: " + str(res))
        assert "result" in res
        assert "status" in res["result"]
        assert "ok" == res["result"]["status"]

def tests():
    VDB_URL = "http://localhost:8081/api/v1"
    VDB_URL_BATCH = VDB_URL + "/batch"
    VDB_HEADER = { "Content-Type" : "application/json" }

    print("\nVDBL sanity tests, URL: " + VDB_URL)

    print("\nTest send/receive commands ...")
    assert len(get_info( VDB_URL )) > 0
    req_id = post_cmd(VDB_URL, VDB_HEADER, "test command;")
    print(
        "waiting: " + str( get_info_waiting( VDB_URL ) ) +
        " done: "  + str( get_info_done( VDB_URL ) )
    )
    print( "req_id: " + req_id )
    assert 0 < get_info_done( VDB_URL ) or 0 < get_info_waiting( VDB_URL )
    assert len(get_cmd( VDB_URL, req_id )) > 0
    
    print("\nTest 1 : create/drop/store/restore ...")
    exec_cmd(VDB_URL, VDB_HEADER, "CREATE COLLECTION doc0 ( VECTOR [ 3 ] );")
    exec_cmd(VDB_URL, VDB_HEADER, 'INSERT INTO doc0 VALUES ( 0.5, 0.5, 0 ) META { "array" : "0.5, 0.5, 0", "date" : "2000.01.01" };')
    exec_cmd(VDB_URL, VDB_HEADER, "STORE COLLECTION doc0;")
    exec_cmd(VDB_URL, VDB_HEADER, "DROP COLLECTION doc0;")

    print("\nTest 2 : search/meta search ...")
    exec_cmd(VDB_URL, VDB_HEADER, "CREATE COLLECTION doc1 ( VECTOR [ 3 ] ) USING FLAT METRIC L2;")
    exec_cmd(VDB_URL, VDB_HEADER, 'INSERT INTO doc1 VALUES ( 1, 0, 0 ) META { "arr" : "1, 0, 0" };')
    exec_cmd(VDB_URL, VDB_HEADER, 'INSERT INTO doc1 VALUES ( 0, 1, 0 ) META { "arr" : "0, 1, 0" };')
    exec_cmd(VDB_URL, VDB_HEADER, 'INSERT INTO doc1 VALUES ( 0.5, 0.5, 0 ) META { "arr" : "0.5, 0.5, 0" };')
    exec_cmd(VDB_URL, VDB_HEADER, "SEARCH FROM doc1 USING ( 1, 0, 0 ) TOP 3;")
    exec_cmd(VDB_URL, VDB_HEADER, "STORE COLLECTION doc1;")
    exec_cmd(VDB_URL, VDB_HEADER, 'META SEARCH FROM doc1 LIKE "arr" ;')
    exec_cmd(VDB_URL, VDB_HEADER, "DROP COLLECTION doc1;")

    print("\nTest 3 : index hnsw ...")
    exec_cmd(VDB_URL, VDB_HEADER, "CREATE COLLECTION doc1 ( VECTOR [ 4 ] ) USING HNSW;")
    exec_cmd(VDB_URL, VDB_HEADER, 'INSERT INTO doc1 VALUES ( 1, 0, 0, 0 );')
    exec_cmd(VDB_URL, VDB_HEADER, 'INSERT INTO doc1 VALUES ( 0, 1, 0, 0 );')
    exec_cmd(VDB_URL, VDB_HEADER, 'INSERT INTO doc1 VALUES ( 0.5, 0.5, 0, 0 ) META { "a" : "0.5, 0.5, 0, 0" };')
    exec_cmds(VDB_URL, VDB_URL_BATCH, VDB_HEADER, [ 
        'INSERT INTO doc1 VALUES ( 0, 0, 0, 1 );',
        'INSERT INTO doc1 VALUES ( 0, 0, 0, 2 );',
        'INSERT INTO doc1 VALUES ( 0, 0, 0, 3 );',
    ] )
    exec_cmd(VDB_URL, VDB_HEADER, "SEARCH FROM doc1 USING ( 1, 0, 0, 0 ) TOP 2;")
    exec_cmd(VDB_URL, VDB_HEADER, "STORE COLLECTION doc1;")
    exec_cmd(VDB_URL, VDB_HEADER, "DROP COLLECTION doc1;")

    print("\nTest 4 : index ivf_hnsw ...")
    exec_cmd(VDB_URL, VDB_HEADER, "CREATE COLLECTION doc1 ( VECTOR [ 2 ] ) USING IVF_HNSW NLIST 2;")
    exec_cmd(VDB_URL, VDB_HEADER, "TRAIN doc1 VALUES ( 1, 0, 2, 3, 4, 5 );") # not enough points
    exec_cmd(VDB_URL, VDB_HEADER, 'INSERT INTO doc1 VALUES ( 1, 0 ) META { "a" : "1, 0" };')
    exec_cmd(VDB_URL, VDB_HEADER, 'INSERT INTO doc1 VALUES ( 0, 1 ) META { "a" : "0, 1" };')
    exec_cmd(VDB_URL, VDB_HEADER, "SEARCH FROM doc1 USING ( 1, 0 ) TOP 2;")
    exec_cmd(VDB_URL, VDB_HEADER, "DROP COLLECTION doc1;")

    #print("\nTest 5 : index ivf_hnsw ...")

    # SUCCESS
    print("\nThe tests were completed successfully\n")

if __name__ == "__main__":
    try:
        tests()
    except Exception as e:
        print(f"FAILED: {e}")
        traceback.print_exc()
        exit(1)
