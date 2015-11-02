from fabric.api import cd, hosts, run, settings, task


@task
@hosts('root@scarlet.fusionapp.com')
def build_slack_better_bitbucket():
    with settings(warn_only=True):
        if run('test -d /srv/build/slack_better_bitbucket').failed:
            run('mkdir -p /srv/build/slack_better_bitbucket')
            run('git clone --quiet https://github.com/jonathanj/slack-better-bitbucket.git /srv/build/slack_better_bitbucket/src')
    with cd('/srv/build/slack_better_bitbucket/src'):
        run('git pull')
        run('docker pull idnar/lein')
        run('docker run --rm --tty --interactive --volume=/srv/build/slack_better_bitbucket/.m2:/root/.m2 --volume=/srv/build/slack_better_bitbucket/.lein:/root/.lein --volume=/srv/build/slack_better_bitbucket/src:/lein idnar/lein uberjar')
        run('docker build --tag=fusionapp/slack_better_bitbucket --file=Dockerfile .')


@task
@hosts('root@scarlet.fusionapp.com')
def deploy():
    with settings(warn_only=True):
        run('docker stop --time=30 slack_better_bitbucket')
        run('docker rm --volumes --force slack_better_bitbucket')
    run('docker run --detach --restart=always --name=slack_better_bitbucket --publish=8880:8880 --publish=8881:8881 --volume=/srv/db/slack_better_bitbucket:/db --workdir=/db fusionapp/slack_better_bitbucket --config=/db/config.json')


@task(default=True)
@hosts('root@scarlet.fusionapp.com')
def build_and_deploy():
    build_slack_better_bitbucket()
    deploy()
