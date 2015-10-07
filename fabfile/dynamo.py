from fabric.api import cd, hosts, run, settings, task


@task
@hosts('root@scarlet.fusionapp.com')
def build_clj_dynamo():
    with settings(warn_only=True):
        if run('test -d /srv/build/clj-dynamo').failed:
            run('mkdir -p /srv/build/clj-dynamo')
            run('git clone --quiet https://github.com/ddormer/clj-dynamo.git /srv/build/clj-dynamo/src')
    with cd('/srv/build/fusion'):
        run('hg pull -u')
        run('docker pull idnar/lein')
        run('docker run --rm --tty --interactive --volume=/srv/build/clj-dynamo/.m2:/root/.m2 --volume=/srv/build/clj-dynamo/.lein:/root/.lein --volume=/srv/build/clj-dynamo/src:/lein idnar/lein uberjar')
