from __future__ import print_function

from sys import version_info

if version_info[0] == 2:
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO
else:
    from io import StringIO

import offregister_circus.ubuntu as circus_mod
import offregister_nginx_static.ubuntu as nginx_static
import offregister_python.ubuntu as python_mod
from fabric.contrib.files import exists
from nginx_parse_emit.emit import api_proxy_block
from nginx_parse_emit.utils import get_parsed_remote_conf, merge_into
from nginxparser import dumps, loads
from offregister_fab_utils.ubuntu.systemd import restart_systemd


def install0(c, *args, **kwargs):
    kwargs.setdefault("virtual_env", "/opt/venvs/airflow")

    if not kwargs.get("skip_virtualenv", False):
        venv0_kwargs = {
            "virtual_env": kwargs["virtual_env"],
            "python3": True,
            "pip_version": "19.2.3",
            "use_sudo": True,
            "remote_user": "ubuntu",
            "PACKAGES": ["apache-airflow[postgres,redis]"],
        }
        venv0_kwargs.update(kwargs)
        python_mod.install_venv0(**venv0_kwargs)

    circus0_kwargs = {
        "APP_NAME": "airflow",
        "APP_PORT": 8080,
        "CMD": "{virtual_env}/bin/airflow".format(virtual_env=kwargs["virtual_env"]),
        "CMD_ARGS": "webserver",
        "WSGI_FILE": None,
    }
    circus0_kwargs.update(kwargs)
    circus_mod.install_circus0(**circus0_kwargs)

    kwargs.setdefault("skip_nginx_restart", True)
    kwargs.setdefault(
        "conf_remote_filename",
        "/etc/nginx/sites-enabled/{}.conf".format(kwargs["SERVER_NAME"]),
    )
    kwargs.update(
        {
            "nginx_conf": "proxy-pass.conf",
            "NAME_OF_BLOCK": "airflow",
            "SERVER_LOCATION": "localhost:{port}".format(
                port=circus0_kwargs["APP_PORT"]
            ),
            "LISTEN_PORT": 80,
            "LOCATION": "/",
        }
    )
    if exists(c, runner=c.run, path=kwargs["conf_remote_filename"]):
        parsed_remote_conf = get_parsed_remote_conf(kwargs["conf_remote_filename"])

        parsed_api_block = loads(
            api_proxy_block(
                location=kwargs["LOCATION"],
                proxy_pass="http://{}".format(kwargs["SERVER_LOCATION"]),
            )
        )
        sio = StringIO()
        sio.write(
            dumps(
                merge_into(kwargs["SERVER_NAME"], parsed_remote_conf, parsed_api_block)
            )
        )
        sio.seek(0)

        c.put(sio, kwargs["conf_remote_filename"], use_sudo=True)
    else:
        nginx_static.setup_custom_conf2(**kwargs)

        env = dict(
            VIRTUAL_ENV=kwargs["virtual_env"],
            PATH="{}/bin:$PATH".format(kwargs["virtual_env"]),
        )
        c.sudo("airflow initdb", env=env)

    restart_systemd(c, "circusd")


__all__ = ["install0"]
