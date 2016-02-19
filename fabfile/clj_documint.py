from fabric.api import cd, hosts, run, settings, task


@task
@hosts('root@scarlet.fusionapp.com')
def build():
    with settings(warn_only=True):
        if run('test -d /srv/build/clj-documint').failed:
            run('mkdir -p /srv/build/clj-documint')
            run('git clone --quiet https://github.com/fusionapp/clj-documint.git /srv/build/clj-documint/src')
    with cd('/srv/build/clj-documint/src'):
        run('git pull')
        run('docker pull idnar/lein')
        run('docker run --rm --tty --interactive --volume=/srv/build/clj-documint/.m2:/root/.m2 --volume=/srv/build/clj-documint/.lein:/root/.lein --volume=/srv/build/clj-documint/src:/lein idnar/lein uberjar')
        run('docker build --tag=fusionapp/clj-documint --file=Dockerfile .')


@task
@hosts('root@scarlet.fusionapp.com')
def deploy():
    with settings(warn_only=True):
        run('docker stop --time=30 clj-documint')
        run('docker rm --volumes --force clj-documint')
    run('docker run --detach --restart=always --name=clj-documint --publish=3000:3000 --volume=/srv/db/clj-documint:/db --workdir=/db fusionapp/clj-documint --config=/db/config.json')


@task(default=True)
@hosts('root@scarlet.fusionapp.com')
def build_and_deploy():
    build()
    deploy()
