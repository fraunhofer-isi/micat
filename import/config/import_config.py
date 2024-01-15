# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import os

import yaml


def get_config():
    with open(os.path.dirname(os.path.realpath(__file__)) + '/config.yaml', 'r', encoding='utf8') as file:
        config = yaml.safe_load(file)
    return config


def get_paths():
    config = get_config()
    public_database_path = config['paths']['public_database']
    raw_data_path = config['paths']['raw_data']
    return public_database_path, raw_data_path
