# © 2024, 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import yaml

from micat.utils import api


def description_by_key(request):
    query = api.parse_request(request)
    try:
        key = query['key']
    except KeyError:
        return "Error: You need to provide a 'key' argument in the request: description?key=foo."

    description_map = descriptions_as_json()
    try:
        value = description_map[key]
        return value
    except KeyError:
        return "Error: Description key '" + key + "' not found"


def descriptions_as_json():
    with open('./data/descriptions.yml', 'r', encoding='utf8') as file:
        descriptions = yaml.safe_load(file)
        return descriptions
