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
import pika

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
    "--port",
    type=int,
    default=config.get("Defaults", "port"),
    help="RabbitMQ port",
)

parser.add_argument(
    "--api_port",
    type=int,
    default=config.get("Defaults", "api_port"),
    help="RabbitMQ Management API port",
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
API_PORT = args.api_port
PORT = args.port
VHOST = args.vhost
QUEUES_API_URL = f"http://{HOST}:{API_PORT}/api/queues"


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

    connection_params = pika.ConnectionParameters(
        host=HOST, port=PORT, virtual_host=VHOST, credentials=pika.PlainCredentials(USERNAME, PASSWORD)
    )

    with pika.BlockingConnection(connection_params) as connection:
        channel = connection.channel()
        for queue in queues:
            if name_pattern.match(queue["name"]) and queue["vhost"] == VHOST:
                if config.getboolean("Actions", "deletion_dry_run", fallback=True):
                    print(
                        f"Would delete queue {queue['name']} on vhost {queue['vhost']}"
                    )
                    continue
                channel.queue_delete(queue['name'])
                print(f"Deleted queue {queue['name']} on vhost {queue['vhost']}")
