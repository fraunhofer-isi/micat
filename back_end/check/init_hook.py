# © 2023 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import os
import sys
from pylint.config import find_default_config_files


def init():
    with open('pylint.log', 'w') as pylint_log:
        pylint_log.write("Initializing pylint with init-hook from pyproject.toml...\\n")
        config_paths = list(find_default_config_files())

        if len(config_paths) > 0:
            config_path = config_paths[0]
            # for PyCharm
            pylint_log.write("Found config path...\\n")
            config_dir = os.path.dirname(config_path)

            sys.path.append(config_dir)

            src_path = config_dir + "/src"
            sys.path.append(src_path)

            test_path = config_dir + "/test"
            sys.path.append(test_path)

            import_path = config_dir + "/test"
            sys.path.append(import_path)

            pylint_log.write("Checking file names...\\n")
            from check.check_file_names import main as check_file_names

            check_file_names()
            pylint_log.write("Finished init-hook.\\n")
        else:
            pylint_log.write("Found no config path...\\n")

            working_directory = os.getcwd()
            pylint_log.write("Current working directory:\\n")
            pylint_log.write(working_directory + "\\n")

            back_end_path = "./back_end"
            if working_directory.endswith("back_end"):
                back_end_path = "."

            # for console
            sys.path.append(back_end_path)
            sys.path.append(back_end_path + "/src")
            sys.path.append(back_end_path + "/test")
            pylint_log.write("Added hard coded paths.\\n")

            pylint_log.write("Checking file names...\\n")
            from check.check_file_names import main as check_file_names

            check_file_names(back_end_path)
            pylint_log.write("Finished init-hook.\\n")
