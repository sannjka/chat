import getpass
from invoke import Exit, Responder
#from invocations.console import confirm
from fabric import task, Connection


REPO_URL = 'https://github.com/sannjka/chat.git'
sudo_pass = getpass.getpass('Your sudo passwor: ')
sudopass = Responder(
    pattern=r'\[sudo\] password',
    response=f'{sudo_pass}\n',
)
sudopass2 = Responder(
    pattern=r'sudo:',
    response=f'{sudo_pass}\n',
)

@task
def depl(c):
    site_folder = f'/home/{c.user}/sites/{c.host}'
    print(dir(c))
    print(c.host)
    print(c.user)
    c.run('ls')
    with c.cd(site_folder):
        #c.run(f'cd {site_folder} && ls')
        c.run('ls')


#from fabric.contrib.files import append, exists, sed
#from fabric.api import env, local, run, put, cd, sudo, get
#
#REPO_URL = 'https://github.com/sannjka/chat.git'
#FILE_NAME = local('echo dump_`date +%d-%m-%Y"_"%H_%M_%S`.sql', capture=True)


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
        #_run_docker_compose(c)
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
    #c.sudo('chmod -R 755 db-data', pty=True, watchers=[sudopass])
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
    c.run(f'sed "s/SITENAME/{c.host}/g" boot.sh >> boot.sh')
    #sed('boot.sh', 'SITENAME', env.host)

#def backup():
#    site_folder = f'/home/{env.user}/sites/{env.host}'
#    if not exists(site_folder):
#        return
#    with cd(site_folder):
#        _make_backup()
#        _retrieve_backup()
#        _remove_backup_on_server()
#        _retrieve_static()
#
#def _make_backup():
#    run("container_name=`docker compose ps | awk '/postgres/{print $1}'` &&"
#        'docker exec -t $container_name pg_dump -c -U postgres -d postgres '
#        f'> {FILE_NAME}')
#
#def _retrieve_backup():
#    get(FILE_NAME, '../')
#
#def _remove_backup_on_server():
#    run(f'rm {FILE_NAME}')
#
#def _retrieve_static():
#    get('static/', '../')
