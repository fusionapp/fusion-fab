from fabric.api import hosts, run, settings, task


@task(default=True)
@hosts('root@scarlet.fusionapp.com')
def deploy():
    run('docker pull registry:2')
    with settings(warn_only=True):
        run('docker stop --time=30 docker-registry')
        run('docker rm --volumes --force docker-registry')
    run(' '.join([
        'docker', 'run',
        '--detach',
        '--restart=always',
        '--name', 'docker-registry',
        '--publish 5000:5000',
        '--volume=/srv/docker-registry:/var/lib/registry',
        '--volume=/srv/certs:/srv/certs:ro',
        '--env REGISTRY_HTTP_TLS_CERTIFICATE=/srv/certs/private/scarlet.fusionapp.com.pem',
        '--env REGISTRY_HTTP_TLS_KEY=/srv/certs/private/scarlet.fusionapp.com.pem',
        '--env REGISTRY_HTTP_TLS_CLIENTCAS=["/srv/certs/public/fusion-ca.crt.pem"]',
        'registry:2'
        ]))
