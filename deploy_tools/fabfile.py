import getpass
from invoke import Responder
from fabric import task


REPO_URL = 'https://github.com/sannjka/chat.git'
sudo_pass = getpass.getpass('Your sudo passwor: ')
sudopass = Responder(
    pattern=r'\[sudo\] password',
    response=f'{sudo_pass}\n',
)


@task
def deploy(c):
    site_folder = f'/home/{c.user}/sites/{c.host}'
    c.run(f'mkdir -p {site_folder}')
    current_commit = c.local('git log -n 1 --format=%H').stdout
    with c.cd(site_folder):
        _get_latest_source_code(c, site_folder, current_commit)
        _update_boot_sh(c)
        _update_static_files(c)
        _create_or_update_donenv(c, site_folder)
        _run_docker_compose(c)
        _make_nginx_conf(c)

def exists(c, path):
    return not c.run(f'test -d {path}', warn=True).failed

def _get_latest_source_code(c, site_folder, current_commit):
    if exists(c, '.git'):
        c.run('git fetch')
    else:
        c.run(f'git clone {REPO_URL} {site_folder}')
    c.run(f'git reset --hard {current_commit}')

def _update_static_files(c):
    c.run('cp -r src/static .')

def _create_or_update_donenv(c, site_folder):
    a = c.put('../.env-docker', site_folder)
    b = c.put('../.env-postgres', site_folder)

def _run_docker_compose(c):
    print('before')
    if exists(c, 'db-data'):
        c.run('sudo chmod -R 755 db-data', pty=True, watchers=[sudopass])
    c.run('docker-compose up -d --build')

def _make_nginx_conf(c):
    c.run(f'sed "s/SITENAME/{c.host}/g" deploy_tools/nginx.template.conf |'
          f' sudo tee /etc/nginx/sites-available/{c.host}',
          pty=True, watchers=[sudopass])
    if not exists(c, f'/etc/nginx/sites-enabled/{c.host}'):
        c.run(f'sudo ln -s /etc/nginx/sites-available/{c.host} '
            f'/etc/nginx/sites-enabled/{c.host}', pty=True, watchers=[sudopass])
    c.run('sudo systemctl restart nginx', pty=True, watchers=[sudopass])

def _update_boot_sh(c):
    c.run(f'sed -i "s/SITENAME/{c.host}/g" boot.sh')
