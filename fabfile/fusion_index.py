from fabric.api import cd, hosts, run, settings, task


@task
@hosts('root@scarlet.fusionapp.com')
def build():
    with settings(use_shell=False, always_use_pty=False):
        with settings(warn_only=True):
            if run('test -d /srv/build/fusion-index').failed:
                run('git clone --quiet --depth 1 -- https://github.com/fusionapp/fusion-index.git /srv/build/fusion-index')
        with cd('/srv/build/fusion-index'):
            run('git fetch --quiet --depth 1')
            run('git reset --hard origin/master')
            run('docker run --rm --volume=/srv/build/fusion-index:/application --volume=/srv/build/fusion-index/wheelhouse:/wheelhouse fusionapp/base')
            run('docker build --tag=fusionapp/fusion-index --file=docker/fusion-index.docker .')
            run('docker tag --force fusionapp/fusion-index scarlet.fusionapp.com:5000/fusionapp/fusion-index')
            run('docker push scarlet.fusionapp.com:5000/fusionapp/fusion-index')


@task
@hosts('root@onyx.fusionapp.com')
def deploy():
    with settings(use_shell=False, always_use_pty=False):
        run('docker pull scarlet.fusionapp.com:5000/fusionapp/fusion-index')
        run('docker tag --force scarlet.fusionapp.com:5000/fusionapp/fusion-index fusionapp/fusion-index')
        with settings(warn_only=True):
            run('docker stop --time=30 fusion-index')
            run('docker rm --volumes --force fusion-index')
        run('docker run --rm --volume=/srv/db/fusion-index:/db --volume=/srv/certs:/srv/certs fusionapp/fusion-index fusion-index --create --ca=/srv/certs/public/fusion-ca.crt.pem --cert=/srv/certs/private/onyx.fusionapp.com.pem')
        run('docker run --detach --restart=always --name=fusion-index --volume=/srv/db/fusion-index:/db --volume=/srv/certs:/srv/certs --publish=8443:8443 --log-driver=none --workdir=/db fusionapp/fusion-index start --pidfile "" --nodaemon')
