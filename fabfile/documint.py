from fabric.api import cd, hosts, run, settings, task
@task
@hosts('root@onyx.fusionapp.com')
def deploy():
    with settings(use_shell=False, always_use_pty=False):
        run('docker pull scarlet.fusionapp.com:5000/fusionapp/documint')
        with settings(warn_only=True):
            run('docker stop --time=30 documint')
            run('docker rm --volumes --force documint')
        run('docker run --detach --restart=always --name=documint '
            '--label=cron.schedule="0 0 0 ? * ?" '
            '--label=cron.action=restart '
            '--volume=/srv/db/documint:/db --publish=8750:8750 '
            'scarlet.fusionapp.com:5000/fusionapp/documint '
            '--keystore=/db/documint_keystore_uat.jks '
            '--password=123456 '
            '--privateKeyPassword=123456')
