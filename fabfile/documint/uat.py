from fabric.api import cd, hosts, run, settings, task


@task
@hosts('root@scarlet.fusionapp.com')
def build():
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


@task
@hosts('root@scarlet.fusionapp.com')
def deploy():
    with settings(warn_only=True):
        run('docker stop --time=30 documint')
        run('docker rm --volumes --force documint')
    run('docker run --detach --restart=always --name=documint --volume=/srv/db/documint:/db --publish=8750:8750 fusionapp/documint --keystore=/db/documint_keystore_uat.jks --password=123456 --privateKeyPassword=123456')


@task(default=True)
@hosts('root@scarlet.fusionapp.com')
def build_and_deploy():
    build()
    deploy()
