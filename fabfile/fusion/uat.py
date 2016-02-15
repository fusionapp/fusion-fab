from fabric.api import cd, hosts, run, settings, task


@task
@hosts('root@scarlet.fusionapp.com')
def build():
    with settings(use_shell=False, always_use_pty=False):
        with settings(warn_only=True):
            if run('test -d /srv/build/fusion/uat').failed:
                run('mkdir -p /srv/build/fusion')
                run('hg clone --quiet ssh://hg@bitbucket.org/fusionapp/fusion /srv/build/fusion/uat')
        with cd('/srv/build/fusion/uat'):
            run('hg pull')
            run('hg update uat')
            run(' '.join([
                'docker', 'run',
                '--rm',
                '--volume', '${PWD}:/src',
                '--workdir', '/src',
                '--entrypoint', '/bin/bash',
                'node:5.6.0-slim',
                '-c', '"npm install && npm run test && npm run dev-build"',
                ]))
            run('mkdir -p /srv/build/fusion/uat/wheelhouse')
            run('cp -u /srv/build/diamond/wheelhouse/diamond*.whl /srv/build/fusion/uat/wheelhouse')
            run('docker run --rm --volume=/srv/build/fusion/uat:/application --volume=/srv/build/fusion/uat/wheelhouse:/wheelhouse fusionapp/base:cpython')
            run('docker build --tag=scarlet.fusionapp.com:5000/fusionapp/fusion:uat --file=docker/fusion.docker .')
            run('docker push scarlet.fusionapp.com:5000/fusionapp/fusion:uat')


@task
@hosts('root@scarlet.fusionapp.com')
def deploy():
    with settings(use_shell=False, always_use_pty=False):
        run('docker pull scarlet.fusionapp.com:5000/fusionapp/fusion:uat')
        with settings(warn_only=True):
            run('docker stop --time=30 fusion')
            run('docker rm --volumes --force fusion')
        run('docker run --rm --volume=/srv/db/fusion:/db --volume=/srv/certs:/srv/certs:ro scarlet.fusionapp.com:5000/fusionapp/fusion:uat upgrade')
        run('docker run --detach --restart=always --name=fusion --volume=/srv/db/fusion:/db --volume=/srv/certs:/srv/certs:ro --publish=80:80 --publish=2233:23 scarlet.fusionapp.com:5000/fusionapp/fusion:uat')


@task
@hosts('root@scarlet.fusionapp.com')
def backup():
    run('/usr/local/bin/fusion-backup fusion /srv/db/fusion s3://s3-eu-west-1.amazonaws.com/backups-eu-uat.fusionapp.com')


@task(default=True)
@hosts('root@scarlet.fusionapp.com')
def build_and_deploy():
    build()
    deploy()
