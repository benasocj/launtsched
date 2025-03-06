#!/usr/bin/env python3
import argparse
import logging
import re
import sys
import os

from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

load_dotenv()

USERNAME = os.getenv("LAUNTEL_USERNAME")
PASSWORD = os.getenv("LAUNTEL_PASSWORD")
BASE_URL = "https://residential.launtel.net.au"


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Pause or unpause a Launtel internet service.",
    )
    parser.add_argument("action", metavar="action", help="must be `pause` or `unpause`")
    parser.add_argument(
        "--service_id",
        metavar="service_id",
        help="must be an integer service id. you can see a list of your services by running this script without this argument.",
        required=False,
        type=int,
    )
    return parser.parse_args()


logging.basicConfig(
    format="%(asctime)s.%(msecs)03d %(levelname)8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
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

serv_id = args.service_id
if serv_id is None:
    logging.info("getting services")
    r = s.get(BASE_URL + "/services")

    services = []

    soup = BeautifulSoup(r.text, "html.parser")
    service_cards = soup.find_all("div", class_="service-card")

    for card in service_cards:
        serv_title = card.find("span", class_="service-title-txt").text
        pause_button = card.find(
            "button", onclick=re.compile(r"(un)?pauseService\((\d+)")
        )
        if pause_button:
            serv_id = int(re.search(r"\d+", pause_button["onclick"]).group())
            services.append((serv_title, serv_id))

    if not services:
        logging.error("could not find any services that can be paused or unpaused")
        sys.exit()

    # If the account only has one service, proceed without asking which
    # service to pause/unpause
    if len(services) == 1:
        logging.info(f"only one service detected - continuing to {args.action}")
        serv_id = services[0][1]
    else:
        for service in services:
            logging.INFO(service[0] + " - " + str(service[1]))
        try:
            serv_id = int(input("Enter the service ID to pause/unpause: "))
        except:
            logging.error("invalid service id entered. it must be an integer.")
            sys.exit()

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
