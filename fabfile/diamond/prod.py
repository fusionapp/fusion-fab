from fabric.api import hosts, run, settings, task


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
