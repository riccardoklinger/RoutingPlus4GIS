import configparser
import os

def getUUID():
    uuid = os.environ.get('UUID')
    if not uuid:
        config = configparser.RawConfigParser()
        config.read('CONFIG.cfg')
        uuid = config.get('Authorization', 'UUID')
    return uuid
