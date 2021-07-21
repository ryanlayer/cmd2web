#!/home/user/cmd2web/cmd2web_env/bin/python3

"""
    Base Admin
    ~~~~~~~~~~

    :created: 11.03.2018 by Jens Diemer, www.jensdiemer.de
    :copyleft: 2018 by the bootstrap_env team, see AUTHORS for more details.
    :license: GNU General Public License v3 or later (GPLv3+), see LICENSE for more details.
"""


import logging
import os
from pathlib import Path

# Bootstrap-Env
import bootstrap_env
from bootstrap_env.admin_shell.normal_shell import AdminShell
from bootstrap_env.admin_shell.path_helper import PathHelper

log = logging.getLogger(__name__)


def main():
    assert "VIRTUAL_ENV" in os.environ, "ERROR: Call me only in a activated virtualenv!"

    base_file = bootstrap_env.__file__
    # print("\nbootstrap_env.__file__: %r\n" % base_file)

    path_helper = PathHelper(
        base_file=base_file,
        boot_filename="boot_bootstrap_env.py",
        admin_filename="bootstrap_env_admin.py",
    )
    # path_helper.print_path()
    # path_helper.assert_all_path()

    if path_helper.normal_mode:
        # Installed in "normal" mode (as Package from PyPi)
        ShellClass = AdminShell
    else:
        # Installed in "developer" mode (as editable from source)
        # Import here, because developer_shell imports packages that
        # only installed in "developer" mode ;)
        from bootstrap_env.admin_shell.developer_shell import DeveloperAdminShell
        ShellClass = DeveloperAdminShell

    ShellClass(
        path_helper,
        self_filename=Path(__file__).name
    ).cmdloop()


if __name__ == '__main__':
    main()
