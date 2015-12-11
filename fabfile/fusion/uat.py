from fabric.api import cd, hosts, run, settings, task


@task
@hosts('root@scarlet.fusionapp.com')
def build():
    with settings(warn_only=True):
        if run('test -d /srv/build/fusion/uat').failed:
            run('mkdir -p /srv/build/fusion')
            run('hg clone --quiet ssh://hg@bitbucket.org/fusionapp/fusion /srv/build/fusion/uat')
    with cd('/srv/build/fusion/uat'):
        run('hg pull')
        run('hg update uat')
        run('docker build --tag=fusionapp/fusion-base:uat --file=docker/base.docker .')
        run('docker build --tag=fusionapp/fusion-build:uat --file=docker/build.docker .')
        run('mkdir -p /srv/build/fusion/uat/wheelhouse')
        run('cp -u /srv/build/documint/wheelhouse/* /srv/build/fusion/uat/wheelhouse')
        run('cp -u /srv/build/diamond/wheelhouse/* /srv/build/fusion/uat/wheelhouse')
        # XXX: This is really dumb, but it should be resolved by merging our
        # fork of Nevow upstream.
        run('rm /srv/build/fusion/uat/wheelhouse/Nevow*')
        run('docker run --rm --tty --interactive --volume=/srv/build/fusion/uat:/application --volume=/srv/build/fusion/uat/wheelhouse:/wheelhouse fusionapp/fusion-build:uat')
        run('docker build --tag=fusionapp/fusion:uat --file=docker/run.docker .')
        run('docker tag -f fusionapp/fusion:uat scarlet.fusionapp.com:5000/fusionapp/fusion:uat')
        run('docker push scarlet.fusionapp.com:5000/fusionapp/fusion:uat', shell=False, pty=False)


@task
@hosts('root@scarlet.fusionapp.com')
def deploy():
    with settings(warn_only=True):
        run('docker stop --time=30 fusion')
        run('docker rm --volumes --force fusion')
    run('docker run --rm --tty --interactive --volume=/srv/db/fusion:/db --volume=/srv/certs:/srv/certs fusionapp/fusion:uat upgrade')
    run('docker run --detach --restart=always --name=fusion --volume=/srv/db/fusion:/db --volume=/srv/certs:/srv/certs --publish=80:80 --publish=2233:23 --workdir=/db fusionapp/fusion:uat')


@task
@hosts('root@scarlet.fusionapp.com')
def backup():
    run('/usr/local/bin/fusion-backup fusion /srv/db/fusion s3://s3-eu-west-1.amazonaws.com/backups-eu-uat.fusionapp.com')


@task(default=True)
@hosts('root@scarlet.fusionapp.com')
def build_and_deploy():
    build()
    deploy()
