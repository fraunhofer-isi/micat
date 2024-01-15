# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later


# https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/220
def is_eurostat_mode(id_mode):
    if isinstance(id_mode, str):
        raise ValueError('id_mode must be passed as number!')
    mode_ids_eurostat = [3, 4]  # Also see https://gitlab.cc-asp.fraunhofer.de/isi/micat/-/issues/220
    if id_mode in mode_ids_eurostat:
        return True

    return False
