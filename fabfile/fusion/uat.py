from fabric.api import cd, hosts, run, settings, task


@task
@hosts('root@scarlet.fusionapp.com')
def build():
    with settings(warn_only=True):
        if run('test -d /srv/build/fusion').failed:
            run('hg clone --quiet ssh://hg@bitbucket.org/fusionapp/fusion /srv/build/fusion')
    with cd('/srv/build/fusion'):
        run('hg pull')
        run('hg update uat')
        run('docker build --tag=fusionapp/fusion-base --file=docker/base.docker .')
        run('docker build --tag=fusionapp/fusion-build --file=docker/build.docker .')
        run('cp -u /srv/build/documint/wheelhouse/* /srv/build/fusion/wheelhouse')
        run('cp -u /srv/build/diamond/wheelhouse/* /srv/build/fusion/wheelhouse')
        # XXX: This is really dumb, but it should be resolved by merging our
        # fork of Nevow upstream.
        run('rm /srv/build/fusion/wheelhouse/Nevow*')
        run('docker run --rm --tty --interactive --volume="/srv/build/fusion:/application" --volume="/srv/build/fusion/wheelhouse:/wheelhouse" fusionapp/fusion-build')
        run('docker build --tag=fusionapp/fusion --file=docker/run.docker .')


@task
@hosts('root@scarlet.fusionapp.com')
def deploy():
    with settings(warn_only=True):
        run('docker stop --time=30 fusion')
        run('docker rm --volumes --force fusion')
    run('docker run --rm --tty --interactive --volume="/srv/db/fusion:/db" fusionapp/fusion upgrade')
    run('docker run --detach --restart=always --name=fusion --volume="/srv/db/fusion:/db" --publish=80:80 --publish=2233:23 --workdir=/db fusionapp/fusion')



@task(default=True)
def build_and_deploy():
    build()
    deploy()
