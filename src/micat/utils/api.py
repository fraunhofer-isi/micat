# © 2024, 2025 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from urllib.parse import parse_qs


def parse_request(http_request):
    query_string = http_request.query_string
    decoded_string = query_string.decode()
    decoded_string = decoded_string.replace('%20&%20', ' & ')
    parsed_string = parse_qs(decoded_string)
    query_parameters = dict(parsed_string)
    query_dict = {k: v[0] for k, v in query_parameters.items()}
    if http_request.content_type is not None:
        if http_request.content_type == 'application/json':
            query_dict['json'] = http_request.json
        else:
            raise AttributeError('Query must include the savings table as an array of arrays in the JSON body')
    return query_dict
