"""
This script deletes all queues that match a certain pattern.
It uses the RabbitMQ Management HTTP API to list all queues
and then deletes the ones that match the pattern.
The pattern is defined by two regular expressions, one for
the queue name and one for the vhost.
"""

import argparse
import configparser
import re

import requests

config = configparser.ConfigParser()
config.read("config.ini")

parser = argparse.ArgumentParser(
    description="RabbitMQ Queues Deleter by Pattern"
)
parser.add_argument(
    "--username",
    type=str,
    default=config.get("Defaults", "username"),
    help="RabbitMQ admin username",
)
parser.add_argument(
    "--password",
    type=str,
    default=config.get("Defaults", "password"),
    help="RabbitMQ admin password",
)
parser.add_argument(
    "--host",
    type=str,
    default=config.get("Defaults", "host"),
    help="RabbitMQ host",
)
parser.add_argument(
    "--vhost",
    type=str,
    default=config.get("Defaults", "vhost"),
    help="RabbitMQ vhost",
)
parser.add_argument(
    "--pattern",
    type=str,
    default=config.get("Queues", "name_regex"),
    help="Queue name regular expression",
)

args = parser.parse_args()

USERNAME = args.username
PASSWORD = args.password
HOST = args.host
VHOST = args.vhost
QUEUES_API_URL = f"{HOST}/api/queues"


def delete_queue(queue_json) -> int:
    """
    Deletes a queue using the RabbitMQ Management HTTP API.

    :param queue_json: The JSON object representing the queue.
    Should be a result of a GET request to the RabbitMQ Management API.
    :return: The status code of the DELETE request.
    """
    delete_url = f"{QUEUES_API_URL}/{VHOST}/{queue_json['name']}"
    delete_response = requests.delete(
        delete_url, auth=(USERNAME, PASSWORD), timeout=5
    )
    return delete_response.status_code


def get_queues() -> list:
    """
    Gets all queues using the RabbitMQ Management HTTP API.

    :return: A list of JSON objects representing the queues.
    :raises Exception: If the request to the RabbitMQ Management API fails.
    """
    response = requests.get(
        QUEUES_API_URL, auth=(USERNAME, PASSWORD), timeout=5
    )
    if response.status_code != 200:
        response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    name_pattern = re.compile(rf"{args.pattern}")

    queues = get_queues()

    for queue in queues:
        if name_pattern.match(queue["name"]) and queue["vhost"] == VHOST:
            if config.getboolean("Actions", "deletion_dry_run", fallback=True):
                print(
                    f"Would delete queue {queue['name']} on vhost {queue['vhost']}"
                )
                continue

            status_code = delete_queue(queue)
            if status_code == 204:
                print(
                    f"Queue {queue['name']} deleted on vhost {queue['vhost']}"
                )
            else:
                print(
                    f"Error deleting queue {queue['name']} on vhost {queue['vhost']}: {status_code}"
                )
