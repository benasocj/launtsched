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
        description="Pause, unpause, or adjust the plan of a Launtel internet service.",
    )
    parser.add_argument(
        "action", metavar="action", help="must be `pause` or `unpause` or `plan`"
    )
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


def get_services():
    logging.info("getting services")
    r = s.get(BASE_URL + "/services")

    services = []

    soup = BeautifulSoup(r.text, "html.parser")
    service_cards = soup.find_all("div", class_="service-card")

    for card in service_cards:
        serv_title = card.find("span", class_="service-title-txt").text
        serv_user_id = (
            card.find("i", class_="fa-bar-chart").parent.get("href").split("=")[2]
        )
        serv_avc_id = card.get("id")
        pause_button = card.find(
            "button", onclick=re.compile(r"(un)?pauseService\((\d+)")
        )
        if pause_button:
            serv_id = int(re.search(r"\d+", pause_button["onclick"]).group())
            services.append((serv_title, serv_id, serv_avc_id, serv_user_id))

    return services


if __name__ == "__main__":
    chosen_service = None

    services = get_services()
    if not services:
        logging.error("could not find any modifiable services on your account")
        sys.exit()

    for service in services:
        if service[1] == args.service_id:
            chosen_service = service
            break

    if args.service_id is not None and chosen_service is None:
        logging.error("could not find a service matching the specified id")
        sys.exit()

    if chosen_service is None:
        if len(services) == 1:
            logging.info(f"only one service detected - continuing to {args.action}")
            chosen_service = services[0]
        else:
            for idx, service in enumerate(services):
                logging.info("#" + str(idx) + ": " + service[0])
            try:
                chosen_idx = int(
                    input("Enter the service # to use for future actions: ")
                )
                chosen_service = services[chosen_idx]
            except:
                logging.error("invalid non-integer service number entered")
                sys.exit()

    if chosen_service is None:
        logging.error("no service chosen")
        sys.exit()

    chosen_service_name = chosen_service[0]
    chosen_service_id = chosen_service[1]
    chosen_service_avcid = chosen_service[2]
    chosen_service_userid = chosen_service[3]

    if args.action == "pause":
        r = s.post("{}/service_pause/{}".format(BASE_URL, chosen_service_id))
        r.raise_for_status()
        logging.info("paused")
    elif args.action == "unpause":
        r = s.post("{}/service_unpause/{}".format(BASE_URL, chosen_service_id))
        r.raise_for_status()
        logging.info("unpaused")
    elif args.action == "plan":
        r = s.get("{}/service?avcid={}".format(BASE_URL, chosen_service_avcid))
        soup = BeautifulSoup(r.text, "html.parser")
        speed_choices = soup.find_all("span", class_="list-group-item")
        for choice in speed_choices:
            col_values = choice.find_all("div", class_="col-sm-4")
            logging.info(
                str(choice.get("data-value")) + ": " + col_values[0].text.strip()
            )
        chosen_service_locid = soup.find("input", {"name": "locid"}).get("value")
        try:
            chosen_psid = int(input("Enter the psid of the new plan you would like: "))
        except:
            logging.error("invalid non-integer psid entered")
            sys.exit()
        r = s.post(
            "{}/confirm_service?userid={}&psid={}&unpause=0&service_id={}&upgrade_options=&discount_code=&avcid={}&locid={}&coat=".format(
                BASE_URL,
                chosen_service_userid,
                chosen_psid,
                chosen_service_id,
                chosen_service_avcid,
                chosen_service_locid,
            )
        )
    else:
        logging.info("no action matched")
