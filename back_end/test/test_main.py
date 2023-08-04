# © 2023 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from main import main
from mock import patch


@patch('builtins.print')
def test_main(mocked_print):
    main()
    mocked_print.assert_called()
