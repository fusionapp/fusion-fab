import uuid

from fabric.api import env, parallel, put, roles, run, task



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



__all__ = ['staticdata']
