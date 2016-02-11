from fabric.api import hosts, run, settings, task


@task
@hosts('root@scarlet.fusionapp.com')
def unwrapper():
    run('docker pull fusionapp/registry-unwrap')
    with settings(warn_only=True):
        run('docker stop --time=30 registry-unwrap')
        run('docker rm --volumes --force registry-unwrap')
    run(' '.join([
        'docker', 'run',
        '--detach',
        '--restart=always',
        '--name', 'registry-unwrap',
        '--publish 5001:5001',
        '--volume=/srv/certs:/srv/certs:ro',
        'fusionapp/registry-unwrap',
        '-T60',
        'OPENSSL-LISTEN:5001,tcpwrap,fork,verify=0,dhparam=/srv/certs/dhparam.pem,cert=/srv/certs/private/scarlet.fusionapp.com-letsencrypt.pem',
        'OPENSSL:scarlet.fusionapp.com:5000,cafile=/srv/certs/public/fusion-ca.crt.pem,cert=/srv/certs/private/scarlet.fusionapp.com.pem',
        ]))


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


@task()
@hosts('root@scarlet.fusionapp.com')
def mirror():
    run('docker pull registry:2')
    with settings(warn_only=True):
        run('docker stop --time=30 docker-registry-mirror')
        run('docker rm --volumes --force docker-registry-mirror')
    run(' '.join([
        'docker', 'run',
        '--detach',
        '--restart=always',
        '--name', 'docker-registry-mirror',
        '--publish 5002:5000',
        '--volume=/srv/docker-registry-mirror:/var/lib/registry',
        '--volume=/srv/certs:/srv/certs:ro',
        '--env REGISTRY_HTTP_TLS_CERTIFICATE=/srv/certs/private/scarlet.fusionapp.com-letsencrypt.pem',
        '--env REGISTRY_HTTP_TLS_KEY=/srv/certs/private/scarlet.fusionapp.com-letsencrypt.pem',
        '--env REGISTRY_PROXY_REMOTEURL=https://registry-1.docker.io',
        'registry:2'
        ]))
