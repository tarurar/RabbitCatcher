# RabbitCatcher

RabbitCatcher is a Python utility designed to manage RabbitMQ queues, specifically focusing on identifying and optionally deleting queues based on a given pattern and virtual host (vhost).

## Features

- **Pattern Matching**: Allows filtering queues by name using regular expressions.
- **Selective Deletion**: Supports dry-run and actual deletion modes for queues that match the criteria.
- **Vhost Support**: Operates within the context of a specified RabbitMQ vhost.

## Configuration

RabbitCatcher relies on a configuration file in INI format to manage its operations. Below is the structure and explanation of the `config.ini` file required for running RabbitCatcher.

### config.ini Structure

```ini
[Defaults]
username = username # Username for RabbitMQ authentication
password = pwd # Password for RabbitMQ authentication
host = host_name:15672 # RabbitMQ server URL
vhost = / # The target vhost

[Queues]
name_regex = .* # Regular expression pattern to match queue names

[Actions]
deletion_dry_run = True # If True, queues will not be deleted. Set to False to enable deletion.