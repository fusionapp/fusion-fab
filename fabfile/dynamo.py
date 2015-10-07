from fabric.api import cd, hosts, run, settings, task


@task
@hosts('root@scarlet.fusionapp.com')
def build_clj_dynamo():
    with settings(warn_only=True):
        if run('test -d /srv/build/clj-dynamo').failed:
            run('mkdir -p /srv/build/clj-dynamo')
            run('git clone --quiet https://github.com/ddormer/clj-dynamo.git /srv/build/clj-dynamo/src')
    with cd('/srv/build/clj-dynamo/src'):
        run('git pull')
        run('docker pull idnar/lein')
        run('docker run --rm --tty --interactive --volume=/srv/build/clj-dynamo/.m2:/root/.m2 --volume=/srv/build/clj-dynamo/.lein:/root/.lein --volume=/srv/build/clj-dynamo/src:/lein idnar/lein uberjar')
        run('docker build --tag=fusionapp/dynamo --file=Dockerfile .')


@task
@hosts('root@scarlet.fusionapp.com')
def deploy():
    with settings(warn_only=True):
        run('docker stop --time=30 dynamo')
        run('docker rm --volumes --force dynamo')
    run('docker run --detach --restart=always --name=dynamo --publish=8080:8080 --volume="/srv/db/dynamo:/db" --workdir=/db fusionapp/dynamo --config /db/config.json')


@task(default=True)
@hosts('root@scarlet.fusionapp.com')
def build_and_deploy():
    build_clj_dynamo()
    deploy()
