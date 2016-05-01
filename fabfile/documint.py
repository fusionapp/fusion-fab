from fabric.api import cd, hosts, run, settings, task


@task
@hosts('root@scarlet.fusionapp.com')
def build():
    with settings(use_shell=False, always_use_pty=False):
        with settings(warn_only=True):
            if run('test -d /srv/build/documint').failed:
                run('git clone --quiet --depth 1 -- https://github.com/fusionapp/documint.git /srv/build/documint')
        with cd('/srv/build/documint'):
            run('git fetch --quiet --depth 1 origin master')
            run('git reset --hard origin/master')
            run('docker run --rm --volume="/srv/build/documint:/application" --volume="/srv/build/documint/wheelhouse:/wheelhouse" fusionapp/base')
            run('cp /srv/build/clj-neon/src/target/uberjar/clj-neon-*-standalone.jar bin/clj-neon.jar')
            run('docker build --tag=scarlet.fusionapp.com:5000/fusionapp/documint --file=docker/documint.docker .')
            run('docker push scarlet.fusionapp.com:5000/fusionapp/documint')


@task
@hosts('root@scarlet.fusionapp.com', 'root@onyx.fusionapp.com')
def deploy():
    with settings(use_shell=False, always_use_pty=False):
        run('docker pull scarlet.fusionapp.com:5000/fusionapp/documint')
        with settings(warn_only=True):
            run('docker stop --time=30 documint')
            run('docker rm --volumes --force documint')
        run('docker run --detach --restart=always --name=documint '
            '--volume=/srv/db/documint:/db --publish=8750:8750 '
            'scarlet.fusionapp.com:5000/fusionapp/documint '
            '--keystore=/db/documint_keystore_uat.jks '
            '--password=123456 '
            '--privateKeyPassword=123456')
