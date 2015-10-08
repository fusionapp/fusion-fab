from fabric.api import cd, hosts, run, settings, task


@task
@hosts('root@scarlet.fusionapp.com')
def build():
    with settings(warn_only=True):
        if run('test -d /srv/build/fusion_index').failed:
            run('git clone --quiet --depth 1 -- https://github.com/fusionapp/fusion-index.git /srv/build/fusion_index')
    with cd('/srv/build/fusion_index'):
        run('git pull --quiet --depth 1')
        run('docker build --tag=fusionapp/fusion-index-base --file=docker/base.docker .')
        run('docker build --tag=fusionapp/fusion-index-build --file=docker/build.docker .')
        run('docker run --rm --interactive --volume=/srv/build/fusion-index:/application --volume=/srv/build/fusion-index/wheelhouse:/wheelhouse fusionapp/fusion-index-build')
        run('docker build --tag=fusionapp/fusion-index --file=docker/run.docker .')


@task
@hosts('root@scarlet.fusionapp.com')
def deploy():
    with settings(warn_only=True):
        run('docker stop --time=30 uat_fusion-index')
        run('docker rm --volumes --force uat_fusion-index')
    run('docker run --rm --interactive --volume=/srv/db/fusion-index:/srv/db --volume=/srv/certs:/srv/certs fusionapp/fusion-index fusion-index --create --ca=/srv/certs/fusion-ca.crt.pem --cert=/srv/certs/private/fusiontest.net-fusionca.crt.pem')
    run('docker run --detach --restart=always --name=uat_fusion-index --volume=/srv/db/fusion-index:/srv/db --publish=8443:8443 --workdir=/srv/db fusionapp/fusion-index')


@task(default=True)
@hosts('root@scarlet.fusionapp.com')
def build_and_deploy():
    build()
    deploy()
