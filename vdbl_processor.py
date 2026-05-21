# VDBL command processor

import json
import asyncio
from typing import Any, AsyncIterator, Awaitable, Callable, Dict
import vdbl_eval
import vdbl_parser
import vdbl_constants as C

# clean unread results
DEFAULT_RESULT_TIMEOUT = 30

# queue requests/results
g_queue = asyncio.Queue()
g_result : Dict[ str, str ] = { }
g_ev = vdbl_eval.Evaluator()

async def process_cmd( cmd : str ) :
    ret = "{}"
    try:
        ast = vdbl_parser.parse( cmd )
        res = g_ev.eval( ast )
        ret = { C.JSTATUS: C.STATUS_OK, C.JRESULT: res }
    except Exception as ex:
        ret = { C.JSTATUS: C.STATUS_FAILED, C.JREASON: str(ex) }
    return ret


async def get_result( req_id : str ) :
    ret = "{}"
    if req_id in g_result:
        ret = g_result[ req_id ]
        del g_result[ req_id ]
    return ret;

async def proc_req( queue ):
    req = await queue.get()
    j = json.loads( req )
    cmd = j[ C.JSTATEMENT ]
    req_id = j[ C.JID ]
    nTO = DEFAULT_RESULT_TIMEOUT
    if C.JTIMEOUT in j:
        nTO = int(j[ C.JTIMEOUT ])
    # processing
    res = await process_cmd( cmd )
    g_result[ req_id ] = json.dumps( res )
    queue.task_done()
    # clean after timeout
    await asyncio.sleep( min(DEFAULT_RESULT_TIMEOUT, nTO) )
    await get_result( req_id )

async def process_waitings( queue ):
    if g_queue.qsize() > 0:
        for i in range(0, g_queue.qsize()):
            asyncio.create_task(proc_req(g_queue))

async def add_req( req : str ):
    await g_queue.put( req )
    await process_waitings(g_queue)

async def add_reqs( reqs ):
    for r in reqs:
        await g_queue.put( r )
    await process_waitings(g_queue)
    
async def get_number_of_results():
    return len(g_result)

async def get_number_of_requests():
    return g_queue.qsize()

