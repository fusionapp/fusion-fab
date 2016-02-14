import os.path
from fabric.api import hosts, run, settings, task


def runEliot(siteDir, suffix, args):
    logfile = 'eliot.log'
    if suffix:
        logfile = ''.join([logfile, '.', suffix])
    with settings(use_shell=False, always_use_pty=False):
        run(' '.join([
            'docker run',
            '--rm',
            '--workdir /logs',
            '--volume', os.path.join(siteDir, 'run/logs') + ':/logs:ro',
            'scarlet.fusionapp.com:5000/fusionapp/fusion-tools',
            'eliot-tree',
            args,
            logfile,
            ]))


@task(name='diamond-uat')
@hosts('root@scarlet.fusionapp.com')
def diamond_uat(suffix='', args=''):
    runEliot('/srv/db/diamond/diamond.axiom', suffix, args)


@task(name='diamond-prod')
@hosts('root@onyx.fusionapp.com')
def diamond_prod(suffix='', args=''):
    runEliot('/srv/db/diamond/diamond.axiom', suffix, args)


@task(name='fusion-uat')
@hosts('root@scarlet.fusionapp.com')
def fusion_uat(suffix='', args=''):
    runEliot('/srv/db/fusion/fusion.axiom', suffix, args)
