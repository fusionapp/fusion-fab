from fabric.api import hosts, run, settings, task


@task(default=True)
@hosts('root@scarlet.fusionapp.com')
def deploy():
    run('docker pull drone/drone:0.4')
    with settings(warn_only=True):
        run('docker stop --time=30 drone')
        run('docker rm --force drone')
    run(' '.join([
        'docker', 'run',
        '--detach',
        '--restart=always',
        '--name', 'drone',
        '--publish=8443:8443',
        '--volume=/srv/drone/lib:/var/lib/drone',
        '--volume=/var/run/docker.sock:/var/run/docker.sock',
        '--volume=/srv/certs:/srv/certs:ro',
        '--volume=/etc/docker/certs.d:/etc/docker/certs.d:ro',
        '--env-file=/srv/drone/dronerc',
        '--env SERVER_ADDR=:8443',
        '--env SERVER_CERT=/srv/certs/private/drone.fusionapp.com.pem',
        '--env SERVER_KEY=/srv/certs/private/drone.fusionapp.com.pem',
        '--env PLUGIN_FILTER="plugins/* fusionapp/*"',
        '--env ESCALATE_FILTER="plugins/drone-docker fusionapp/drone-docker"',
        '--env DEBUG=true',
        'drone/drone:0.4'
        ]))
