#
# Python REST server
#
#   Process vector db commands (vdbl)
#   Return async json results

import json
import argparse
import asyncio
import uuid
import logging
from pathlib import Path
from typing import Any, AsyncIterator, Awaitable, Callable, Dict
from aiohttp import web
import vdbl_processor as processor
import vdbl_constants as C

router = web.RouteTableDef()
logger = logging.getLogger(__name__)

def handle_json_error(
    func: Callable[[web.Request], Awaitable[web.Response]]
) -> Callable[[web.Request], Awaitable[web.Response]]:
    async def handler(request: web.Request) -> web.Response:
        try:
            return await func(request)
        except asyncio.CancelledError:
            raise
        except Exception as ex:
            return web.json_response(
                { C.JSTATUS: C.STATUS_FAILED, C.JREASON: str(ex)}, status=400
            )

    return handler

def handle_json_response( web, jsonData ):
    logger.debug("response=" + str(jsonData))
    return web.json_response( jsonData, status=200 )
    
@router.get("/")
async def root(request: web.Request) -> web.Response:
    return web.Response(text=f"vdbl")

@router.post("/api/v1")
@handle_json_error
async def api_new_post(request: web.Request) -> web.Response:
    post = await request.json()
    logger.debug("post=" + str(post))
    cmd = post[ C.JSTATEMENT ]
    to = C.DEFAULT_TO
    if C.JTIMEOUT in post:
        to = post[ C.JTIMEOUT ]
    req_id = str(uuid.uuid4());
    jobj = {
        C.JSTATEMENT: cmd,
        C.JTIMEOUT: to,
        C.JID: req_id
    }
    await processor.add_req(json.dumps(jobj))
    return handle_json_response( web,
        {
            C.JSTATUS: C.STATUS_OK,
            C.JDATA: {
                C.JSTATEMENT: cmd,
                C.JID: req_id               
            },
        }
    )

@router.post("/api/v1/batch")
@handle_json_error
async def api_new_post(request: web.Request) -> web.Response:
    post = await request.json()
    logger.debug("post=" + str(post))
    cmds = post[ C.JSTATEMENTS ]
    to = C.DEFAULT_TO
    if C.JTIMEOUT in post:
        to = post[ C.JTIMEOUT ]
    req_ids = [ ]
    jobjs = [ ]
    for cmd in cmds:
        req_id = str(uuid.uuid4());
        req_ids.append( req_id )
        jobj = {
            C.JSTATEMENT: cmd,
            C.JTIMEOUT: to,
            C.JID: req_id
        }
        jobjs.append( json.dumps(jobj) )
    await processor.add_reqs( jobjs )
    return handle_json_response( web,
        {
            C.JSTATUS: C.STATUS_OK,
            C.JDATA: {
                C.JSTATEMENTS: cmds,
                C.JIDS: req_ids               
            },
        }
    )

@router.get("/api/v1")
@handle_json_error
async def api_get_post(request: web.Request) -> web.Response:
    nWaiting = await processor.get_number_of_requests()
    nDone = await processor.get_number_of_results()
    return handle_json_response( web,
        {
            C.JSTATUS: C.STATUS_OK,
            C.JWAITING: nWaiting,
            C.JDONE: nDone,
        }
    )

@router.get("/api/v1/{post}")
@handle_json_error
async def api_get_post(request: web.Request) -> web.Response:
    req_id = request.match_info["post"]
    ret = await processor.get_result(req_id)
    return handle_json_response( web,
        {
            C.JSTATUS: C.STATUS_OK,
            C.JDATA: {
                C.JID: req_id,
                C.JRESULT: json.loads( ret )
            },
        }
    )

async def app_close():
    pass

async def init(app: web.Application) -> AsyncIterator[None]:
    yield
    await app_close()

async def init_app() -> web.Application:
    app = web.Application()
    app.add_routes(router)
    app.cleanup_ctx.append(init)
    return app

