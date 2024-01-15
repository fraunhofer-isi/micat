# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import pandas as pd

from calculation.indoor_climate import indoor_climate

some_input = pd.DataFrame([{'year': 2020, 'value': 1}, {'year': 2030, 'value': 1}])
some_input.set_index('year', inplace=True)


def test_indoor_climate():
    result = indoor_climate(some_input)
    values = result['value']
    assert values[2020] == 1
    assert values[2030] == 1
