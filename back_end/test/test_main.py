from main import main
from mock import patch


@patch('builtins.print')
def test_main(mocked_print):
    main()
    mocked_print.assert_called()
