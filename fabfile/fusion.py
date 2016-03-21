import uuid

from fabric.api import env, hosts, parallel, put, roles, run, settings, task



@task(default=True)
@hosts('root@onyx.fusionapp.com')
def deploy():
    with settings(use_shell=False, always_use_pty=False):
        run('docker pull scarlet.fusionapp.com:5000/fusionapp/fusion:prod')
        with settings(warn_only=True):
            run('docker stop --time=30 fusion-prod')
            run('docker rm --volumes --force fusion-prod')
        run(' '.join([
            'docker', 'run',
            '--rm',
            '--env', 'FUSION_PRODUCTION=1',
            '--volume', '/srv/db/fusion:/db',
            '--volume', '/srv/certs:/srv/certs:ro',
            'scarlet.fusionapp.com:5000/fusionapp/fusion:prod',
            'upgrade',
            ]))
        run(' '.join([
            'docker', 'run',
            '--detach',
            '--restart', 'always',
            '--name', 'fusion-prod',
            '--env', 'FUSION_PRODUCTION=1',
            '--volume', '/srv/db/fusion:/db',
            '--volume', '/srv/certs:/srv/certs:ro',
            '--publish', '41.72.130.249:8001:80',
            '--publish', '41.72.130.249:2233:2233',
            'scarlet.fusionapp.com:5000/fusionapp/fusion:prod',
            ]))


@task
@roles('fusion-uat', 'fusion-prod')
@parallel
def staticdata(type, file):
    # This is a bit brittle
    if env.host == 'scarlet.fusionapp.com':
        image = 'scarlet.fusionapp.com:5000/fusionapp/fusion:uat'
    elif env.host == 'onyx.fusionapp.com':
        image = 'scarlet.fusionapp.com:5000/fusionapp/fusion:prod'
    else:
        raise RuntimeError('Unrecognized host {}'.format(env.host))

    tmpdir = '/tmp/{}'.format(uuid.uuid4().hex)
    tmpfile = '{}/data'.format(tmpdir)
    run('mkdir {}'.format(tmpdir))
    put(file, tmpfile)
    run(' '.join([
        'docker', 'run',
        '--rm',
        '--volume', '/srv/db/fusion:/db',
        '--volume', '/srv/certs:/srv/certs:ro',
        '--volume', '{}:/staticdata:ro'.format(tmpdir),
        image,
        'fusion',
        'staticdata',
        type,
        '/staticdata/data',
        ]))
    run('rm -rf {}'.format(tmpdir))



__all__ = ['deploy', 'staticdata']
