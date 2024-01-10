# © 2023 - 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import pandas as pd


def main():
    df = pd.DataFrame([{'id_foo': 1, '2000': 1}])
    value = df['2000'][0]
    print('Hello world ' + str(value))


if __name__ == '__main__':
    main()
