from fabric.api import cd, hosts, run, settings


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


@hosts('root@scarlet.fusionapp.com')
def build_uat_documint():
    with settings(warn_only=True):
        if run('test -d /srv/build/documint').failed:
            run('git clone --quiet -- https://github.com/fusionapp/documint.git /srv/build/documint')
    with cd('/srv/build/documint'):
        run('git pull --quiet')
        run('docker build --tag=fusionapp/documint-base --file=docker/base.docker .')
        run('docker build --tag=fusionapp/documint-build --file=docker/build.docker .')
        run('docker run --rm --tty --interactive --volume="/srv/build/documint:/application" --volume="/srv/build/documint/wheelhouse:/wheelhouse" fusionapp/documint-build')
        run('cp /srv/build/clj-neon/src/target/uberjar/clj-neon-*-standalone.jar bin/clj-neon.jar')
        run('docker build --tag=fusionapp/documint --file=docker/run.docker .')


@hosts('root@scarlet.fusionapp.com')
def deploy_uat_documint():
    with settings(warn_only=True):
        run('docker stop --time=30 documint')
        run('docker rm --volumes --force documint')
    run('docker run --detach --restart=always --name=documint --volume=/srv/db/documint:/db --publish=8750:8750 fusionapp/documint --keystore=/db/documint_keystore_uat.jks --password=123456 --privateKeyPassword=123456')


@hosts('root@scarlet.fusionapp.com')
def build_uat_diamond():
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


@hosts('root@scarlet.fusionapp.com')
def deploy_uat_diamond():
    with settings(warn_only=True):
        run('docker stop --time=30 diamond')
        run('docker rm --volumes --force diamond')
    run('docker run --rm --tty --interactive --volume="/srv/db/diamond:/db" fusionapp/diamond upgrade')
    run('docker run --detach --restart=always --name=diamond --volume="/srv/db/diamond:/db" --publish=443:443 --publish=8021:8021 --workdir=/db fusionapp/diamond')


@hosts('root@scarlet.fusionapp.com')
def build_uat_fusion():
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


@hosts('root@scarlet.fusionapp.com')
def deploy_uat_fusion():
    with settings(warn_only=True):
        run('docker stop --time=30 fusion')
        run('docker rm --volumes --force fusion')
    run('docker run --rm --tty --interactive --volume="/srv/db/fusion:/db" fusionapp/fusion upgrade')
    run('docker run --detach --restart=always --name=fusion --volume="/srv/db/fusion:/db" --publish=80:80 --publish=2233:23 --workdir=/db fusionapp/fusion')


@hosts('root@scarlet.fusionapp.com')
def build_uat():
    build_clj_neon()
    build_uat_documint()
    build_uat_diamond()
    build_uat_fusion()


@hosts('root@scarlet.fusionapp.com')
def deploy_uat():
    deploy_uat_documint()
    deploy_uat_diamond()
    deploy_uat_fusion()


@hosts('root@scarlet.fusionapp.com')
def update_uat():
    build_uat()
    deploy_uat()
