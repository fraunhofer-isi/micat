from main import main
from mock import MagicMock, call, patch


@patch('builtins.print')
def test_main(mocked_print):
    main()
    mocked_print.assert_called()
