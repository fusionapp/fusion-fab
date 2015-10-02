from fabric.api import cd, hosts, run, settings, task


@task
@hosts('root@scarlet.fusionapp.com')
def build_clj_neon():
    with settings(warn_only=True):
        if run('test -d /srv/build/clj-neon').failed:
            run('mkdir -p /srv/build/clj-neon')
            run('hg clone --quiet https://bitbucket.org/fusionapp/clj-neon /srv/build/clj-neon/src')
    with cd('/srv/build/fusion'):
        run('hg pull -u')
        run('docker pull idnar/lein')
        run('docker run --rm --tty --interactive --volume=/srv/build/clj-neon/.m2:/root/.m2 --volume=/srv/build/clj-neon/.lein:/root/.lein --volume=/srv/build/clj-neon/src:/lein idnar/lein uberjar')


@task
@hosts('root@scarlet.fusionapp.com')
def build():
    with settings(warn_only=True):
        if run('test -d /srv/build/diamond').failed:
            run('hg clone --quiet ssh://hg@bitbucket.org/fusionapp/diamond /srv/build/diamond')
    with cd('/srv/build/diamond'):
        run('hg pull')
        run('hg update uat')
        run('docker build --tag=fusionapp/diamond-base --file=docker/base.docker .')
        run('docker build --tag=fusionapp/diamond-build --file=docker/build.docker .')
        run('docker run --rm --tty --interactive --volume="/srv/build/diamond:/application" --volume="/srv/build/diamond/wheelhouse:/wheelhouse" fusionapp/diamond-build')
        run('cp /srv/build/clj-neon/src/target/uberjar/clj-neon-*-standalone.jar bin/clj-neon.jar')
        run('docker build --tag=fusionapp/diamond --file=docker/run.docker .')


@task
@hosts('root@scarlet.fusionapp.com')
def deploy():
    with settings(warn_only=True):
        run('docker stop --time=30 diamond')
        run('docker rm --volumes --force diamond')
    run('docker run --rm --tty --interactive --volume="/srv/db/diamond:/db" fusionapp/diamond upgrade')
    run('docker run --detach --restart=always --name=diamond --volume="/srv/db/diamond:/db" --publish=443:443 --publish=8021:8021 --workdir=/db fusionapp/diamond')


@task(default=True)
@hosts('root@scarlet.fusionapp.com')
def build_and_deploy():
    build()
    deploy()
