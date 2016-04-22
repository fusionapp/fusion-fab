from fabric.api import hosts, run, settings, task


@task
@hosts('root@scarlet.fusionapp.com', 'root@onyx.fusionapp.com')
def deploy():
    with settings(use_shell=False, always_use_pty=False):
        run('docker pull scarlet.fusionapp.com:5000/fusionapp/clj-documint:master')
        with settings(warn_only=True):
            run('docker stop --time=30 clj-documint')
            run('docker rm --volumes --force clj-documint')
        run('docker run --detach --restart=always --name=clj-documint '
            '--publish 3000:3000 --publish 127.0.0.1:3001:3001 '
            '--volume=/srv/db/clj-documint:/db --workdir=/db '
            '--entrypoint /usr/bin/java '
            'scarlet.fusionapp.com:5000/fusionapp/clj-documint:master '
            '-XX:+UseParNewGC -XX:MinHeapFreeRatio=5 -XX:MaxHeapFreeRatio=10 '
            '-XX:+PrintGCTimeStamps -XX:+PrintGCDetails '
            '-Dcom.sun.management.jmxremote.port=3001 '
            '-Dcom.sun.management.jmxremote.rmi.port=3001 '
            '-Dcom.sun.management.jmxremote.ssl=false '
            '-Dcom.sun.management.jmxremote.authenticate=false '
            '-Dcom.sun.management.jmxremote.local.only=false '
            '-Djava.rmi.server.hostname=localhost '
            '-jar /srv/clj-documint/clj-documint.jar')
