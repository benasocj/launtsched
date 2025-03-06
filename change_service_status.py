#!/usr/bin/env python3
import argparse
import logging
import re
import sys

import requests

USERNAME = "foo@example.com"
PASSWORD = "foobar"
BASE_URL = "https://residential.launtel.net.au"


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Pause or unpause a Launtel internet service.",
    )
    parser.add_argument("action", metavar="action", help="must be `pause` or `unpause`")
    return parser.parse_args()


logging.basicConfig(
    format="%(asctime)s.%(msecs)03d %(levelname)8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
    stream=sys.stdout,
)

args = parse_args()
s = requests.Session()
s.headers = {"Accept-Encoding": "gzip"}

logging.info("logging in")
r = s.post(
    BASE_URL + "/login",
    data={"username": USERNAME, "password": PASSWORD},
    allow_redirects=False,
)
if r.status_code != requests.codes.found:
    logging.error("login failed")
    sys.exit()

logging.info("getting services")
r = s.get(BASE_URL + "/services")
js_str = r'onclick="(un)?pauseService\((\d+)'
try:
    serv_id = int(re.search(js_str, r.text).group(2))
# ``ValueError`` in case ``int(...)`` fails
# ``AttributeError`` in case ``re.search`` was unsuccessful
except (AttributeError, ValueError):
    logging.error("could not find service ID")
    sys.exit()
logging.info("service ID: %s", serv_id)

if args.action == "pause":
    r = s.post("{}/service_pause/{}".format(BASE_URL, serv_id))
    r.raise_for_status()
    logging.info("paused")
elif args.action == "unpause":
    r = s.post("{}/service_unpause/{}".format(BASE_URL, serv_id))
    r.raise_for_status()
    logging.info("unpaused")
else:
    logging.info("no action matched")
