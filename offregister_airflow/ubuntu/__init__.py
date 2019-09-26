from __future__ import print_function

import offregister_circus.ubuntu as circus_mod
import offregister_python.ubuntu as python_mod


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
        'APP_PORT': 8045,
        'CMD': '{virtual_env}/bin/airflow'.format(virtual_env=kwargs['virtual_env']),
        'CMD_ARGS': 'webserver',
        'WSGI_FILE': None
    }
    circus0_kwargs.update(kwargs)
    circus_mod.install_circus0(**circus0_kwargs)
