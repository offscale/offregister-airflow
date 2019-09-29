from __future__ import print_function

import offregister_circus.ubuntu as circus_mod
import offregister_nginx_static.ubuntu as nginx_static
import offregister_python.ubuntu as python_mod
from fabric.context_managers import shell_env
from fabric.operations import sudo
from offregister_fab_utils.ubuntu.systemd import restart_systemd


def install0(*args, **kwargs):
    kwargs.setdefault('virtual_env', '/opt/venvs/airflow')

    if not kwargs.get('skip_virtualenv', False):
        venv0_kwargs = {
            'virtual_env': kwargs['virtual_env'],
            'python3': True,
            'pip_version': '19.2.3',
            'use_sudo': True,
            'remote_user': 'ubuntu',
            'PACKAGES': [
                'apache-airflow[postgres,redis]'
            ]
        }
        venv0_kwargs.update(kwargs)
        python_mod.install_venv0(**venv0_kwargs)

    circus0_kwargs = {
        'APP_NAME': 'airflow',
        'APP_PORT': 8080,
        'CMD': '{virtual_env}/bin/airflow'.format(virtual_env=kwargs['virtual_env']),
        'CMD_ARGS': 'webserver',
        'WSGI_FILE': None
    }
    circus0_kwargs.update(kwargs)
    circus_mod.install_circus0(**circus0_kwargs)

    kwargs.setdefault('skip_nginx_restart', True)
    kwargs.setdefault('conf_remote_filename', '/etc/nginx/sites-enabled/{}.conf'.format(kwargs['SERVER_NAME']))
    kwargs.update({
        'nginx_conf': 'proxy-pass.conf',
        'NAME_OF_BLOCK': 'airflow',
        'SERVER_LOCATION': 'localhost:{port}'.format(port=circus0_kwargs['APP_PORT']),
        'LISTEN_PORT': 80,
        'LOCATION': '/'
    })
    nginx_static.setup_conf0(**kwargs)

    with shell_env(VIRTUAL_ENV=kwargs['virtual_env'], PATH="{}/bin:$PATH".format(kwargs['virtual_env'])):
        sudo('airflow initdb')

    restart_systemd('circusd')
