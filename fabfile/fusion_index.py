from fabric.api import cd, hosts, run, settings, task


@task(default=True)
@hosts('root@onyx.fusionapp.com')
def deploy():
    with settings(use_shell=False, always_use_pty=False):
        run('docker pull scarlet.fusionapp.com:5000/fusionapp/fusion-index:master')
        with settings(warn_only=True):
            run('docker stop --time=30 fusion-index')
            run('docker rm --volumes --force fusion-index')
            run('docker run --rm --volume=/srv/db/fusion-index:/db --volume=/srv/certs:/srv/certs:ro scarlet.fusionapp.com:5000/fusionapp/fusion-index:master fusion-index --create --ca=/srv/certs/public/fusion-ca.crt.pem --cert=/srv/certs/private/onyx.fusionapp.com.pem')
            run('docker run --detach --restart=always --name=fusion-index --volume=/srv/db/fusion-index:/db --volume=/srv/certs:/srv/certs:ro --publish=8443:8443 --log-driver=none scarlet.fusionapp.com:5000/fusionapp/fusion-index:master start --pidfile "" --nodaemon')
