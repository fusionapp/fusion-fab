from fabric.api import cd, hosts, run, settings, task


@task
@hosts('root@scarlet.fusionapp.com')
def build():
    with settings(warn_only=True):
        if run('test -d /srv/build/fusion-util').failed:
            run('git clone --quiet --depth 1 -- https://github.com/fusionapp/fusion-util.git /srv/build/fusion-util')
    with cd('/srv/build/fusion-util'):
        run('git pull --quiet --depth 1')
        run('docker build --tag=fusionapp/fusion-tools --file=docker/tools.docker .')
