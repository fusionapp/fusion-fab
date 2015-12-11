from fabric.api import cd, hosts, run, settings, task


@task
@hosts('root@scarlet.fusionapp.com')
def build():
    with settings(use_shell=False, always_use_pty=False):
        with settings(warn_only=True):
            if run('test -d /srv/build/entropy').failed:
                run('git clone --quiet --depth 1 -b 26-repair -- https://github.com/fusionapp/entropy.git /srv/build/entropy')
        with cd('/srv/build/entropy'):
            run('git fetch --quiet --depth 1 origin 26-repair')
            run('git reset --hard origin/26-repair')
            run('docker build --tag=fusionapp/entropy-base --file=docker/base.docker .')
            run('docker build --tag=fusionapp/entropy-build --file=docker/build.docker .')
            run('docker run --rm --volume=/srv/build/entropy:/application --volume=/srv/build/entropy/wheelhouse:/wheelhouse fusionapp/entropy-build')
            run('docker build --tag=fusionapp/entropy --file=docker/run.docker .')
            run('docker tag -f fusionapp/entropy scarlet.fusionapp.com:5000/fusionapp/entropy')
            run('docker push scarlet.fusionapp.com:5000/fusionapp/entropy')


@task
@hosts('root@onyx.fusionapp.com')
def deploy():
    with settings(use_shell=False, always_use_pty=False):
        run('docker pull scarlet.fusionapp.com:5000/fusionapp/entropy')
        run('docker tag -f scarlet.fusionapp.com:5000/fusionapp/entropy fusionapp/entropy')
        with settings(warn_only=True):
            run('docker stop --time=30 entropy')
            run('docker rm --volumes --force entropy')
        run('docker run --detach --restart=always --name=entropy --volume=/srv/db/entropy:/db --publish=8000:8000 --workdir=/db fusionapp/entropy')
