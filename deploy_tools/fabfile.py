from fabric.contrib.files import append, exists, sed
from fabric.api import env, local, run, put, cd, sudo, get

REPO_URL = 'https://github.com/sannjka/chat.git'
FILE_NAME = local('echo dump_`date +%d-%m-%Y"_"%H_%M_%S`.sql', capture=True)


def deploy():
    site_folder = f'/home/{env.user}/sites/{env.host}'
    run(f'mkdir -p {site_folder}')
    with cd(site_folder):
        _get_latest_source_code(site_folder)
        _create_directory_structure_id_necessary()
        _update_boot_sh()
        _update_virtualenv()
        _update_static_files()
        _create_or_update_donenv()
        _run_docker_compose()
        _make_nginx_conf()

def _create_directory_structure_id_necessary():
    pass

def _get_latest_source_code(site_folder):
    if exists('.git'):
        run('git fetch')
    else:
        run(f'git clone {REPO_URL} {site_folder}')
    current_commit = local('git log -n 1 --format=%H', capture=True)
    run(f'git reset --hard {current_commit}')

def _update_virtualenv():
    pass

def _update_static_files():
    run('cp -r app/static .')

def _create_or_update_donenv():
    put('../.env', './')
    put('../.env-postgres', './')

def _run_docker_compose():
    sudo('chmod -R 755 db-data')
    run('docker compose up -d --build')

def _make_nginx_conf():
    sudo(f'sed "s/SITENAME/{env.host}/g" deploy_tools/nginx.template.conf |'
        f' sudo tee /etc/nginx/sites-available/{env.host}')
    if not exists(f'/etc/nginx/sites-enabled/{env.host}'):
        sudo(f'sudo ln -s /etc/nginx/sites-available/{env.host} '
            f'/etc/nginx/sites-enabled/{env.host}')
    sudo('sudo systemctl restart nginx')

def _update_boot_sh():
    sed('boot.sh', 'SITENAME', env.host)

def backup():
    site_folder = f'/home/{env.user}/sites/{env.host}'
    if not exists(site_folder):
        return
    with cd(site_folder):
        _make_backup()
        _retrieve_backup()
        _remove_backup_on_server()
        _retrieve_static()

def _make_backup():
    run("container_name=`docker compose ps | awk '/postgres/{print $1}'` &&"
        'docker exec -t $container_name pg_dump -c -U postgres -d postgres '
        f'> {FILE_NAME}')

def _retrieve_backup():
    get(FILE_NAME, '../')

def _remove_backup_on_server():
    run(f'rm {FILE_NAME}')

def _retrieve_static():
    get('static/', '../')
