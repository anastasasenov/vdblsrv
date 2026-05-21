#
# Python REST server
#
#   Process vector db commands (vdbl)
#   Return async json results

import json
import argparse
import logging
import vdbl_api as api

# globals
DB_FOLDER = "."

def main():
    
    global DB_FOLDER

    SRV_VERSION_MAJOR = 1
    SRV_VERSION_MINOR = 1
    SRV_PORT = 8081
    SRV_HOST = "0.0.0.0"
    #DB_FOLDER = "."
    LOG_FILE = "vdblsrv.log"
    LOG_LEVEL = logging.DEBUG
    SRV_TITLE = "Vector Database Server ( vdbl ) "
    SRV_TITLE += str(SRV_VERSION_MAJOR) + "." + str(SRV_VERSION_MINOR)

    print( SRV_TITLE )
    
    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", help = "server address, default: " + SRV_HOST)
    parser.add_argument("-d", help = "database folder, default: " + DB_FOLDER)    
    parser.add_argument("-f", help = "log file, default: " + LOG_FILE)
    parser.add_argument("-l", help = "log level, default: " + str(LOG_LEVEL))
    parser.add_argument("-p", help = "server port, default: " + str(SRV_PORT))
    sArgs = parser.parse_args()
    if sArgs.p:
        SRV_PORT = int(sArgs.p)
    if sArgs.a:
        SRV_HOST = str(sArgs.a).strip()
    if sArgs.d:
        DB_FOLDER = str(sArgs.d).strip()
    if sArgs.f:
        LOG_FILE = str(sArgs.f).strip()
    if sArgs.l:
        LOG_LEVEL = int(sArgs.l)

    logging.basicConfig(filename=LOG_FILE, level=LOG_LEVEL)
    logger = logging.getLogger(__name__)
    logger.info(SRV_TITLE)
    logger.info("server address:port " + SRV_HOST + ":" + str(SRV_PORT))
    logger.info("database folder: " + DB_FOLDER)
    logger.info("log file: " + LOG_FILE + " level: " + str(LOG_LEVEL))
    logger.info("Started")
    api.web.run_app( api.init_app(), port=SRV_PORT, host=SRV_HOST )
    logger.info("Finished")
