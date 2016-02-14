from fabric.api import cd, hosts, run, settings, task


@task
@hosts('root@scarlet.fusionapp.com')
def build():
    with settings(use_shell=False, always_use_pty=False):
        with settings(warn_only=True):
            if run('test -d /srv/build/diamond-prod').failed:
                run('hg clone --quiet ssh://hg@bitbucket.org/fusionapp/diamond /srv/build/diamond-prod')
        with cd('/srv/build/diamond-prod'):
            run('hg pull')
            run('hg update prod')
            run('docker run --rm --volume=/srv/build/diamond-prod:/application --volume=/srv/build/diamond-prod/wheelhouse:/wheelhouse fusionapp/base')
            run('cp /srv/build/clj-neon/src/target/uberjar/clj-neon-*-standalone.jar bin/clj-neon.jar')
            run('docker build --tag=fusionapp/diamond:prod --file=docker/diamond.docker .')
            run('docker tag --force fusionapp/diamond:prod scarlet.fusionapp.com:5000/fusionapp/diamond:prod')
            run('docker push scarlet.fusionapp.com:5000/fusionapp/diamond:prod')


@task
@hosts('root@onyx.fusionapp.com')
def deploy():
    with settings(use_shell=False, always_use_pty=False):
        run('docker pull scarlet.fusionapp.com:5000/fusionapp/diamond:prod')
        run('docker tag --force scarlet.fusionapp.com:5000/fusionapp/diamond:prod fusionapp/diamond:prod')
        with settings(warn_only=True):
            run('docker stop --time=30 diamond')
            run('docker rm --volumes --force diamond')
        run('docker run --rm --env DIAMOND_PROD=1 --env PYRSISTENT_NO_C_EXTENSION=1 --volume=/srv/db/diamond:/db --volume=/srv/certs:/srv/certs fusionapp/diamond:prod upgrade')
        run('docker run --detach --restart=always --name=diamond --env DIAMOND_PROD=1 --env PYRSISTENT_NO_C_EXTENSION=1 --volume=/srv/db/diamond:/db --volume=/srv/certs:/srv/certs --publish=41.72.130.254:443:443 --publish=41.72.130.254:8021:8021 --workdir=/db fusionapp/diamond:prod')
