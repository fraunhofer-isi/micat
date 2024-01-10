# © 2023 - 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from mock import patch

from main import main


@patch('builtins.print')
def test_main(mocked_print):
    main()
    mocked_print.assert_called()
