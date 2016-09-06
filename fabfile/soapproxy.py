from fabric.api import hosts, run, settings, task


@task(default=True)
@hosts('root@onyx.fusionapp.com')
def deploy():
    run('docker pull fusionapp/soapproxy')
    with settings(warn_only=True):
        run('docker stop --time=30 soapproxy-sbvaf-1 soapproxy-sbvaf-2 soapproxy-sbvaf-3 soapproxy-sbvaf-4 soapproxy-sbvaf-5 soapproxy-absa-1 soapproxy-absa-2')
        run('docker rm --force soapproxy-sbvaf-1 soapproxy-sbvaf-2 soapproxy-sbvaf-3 soapproxy-sbvaf-4 soapproxy-sbvaf-5 soapproxy-absa-1 soapproxy-absa-2')
    run(' '.join([
        'docker', 'run',
        '--detach',
        '--restart=always',
        '--name', 'soapproxy-sbvaf-1',
        '--publish 8080:8080',
        '--volume=/srv/certs:/srv/certs:ro',
        'fusionapp/soapproxy',
        '--endpoint',
        'ssl:8080:privateKey=/srv/certs/private/star.fusionapp.com.pem:extraCertChain=/srv/certs/private/star.fusionapp.com.pem',
        '--uri', 'https://196.8.131.140:13204',
        '--no-verify-tls',
        ]))
    run(' '.join([
        'docker', 'run',
        '--detach',
        '--restart=always',
        '--name', 'soapproxy-sbvaf-2',
        '--publish 8081:8081',
        '--volume=/srv/certs:/srv/certs:ro',
        'fusionapp/soapproxy',
        '--endpoint',
        'ssl:8081:privateKey=/srv/certs/private/star.fusionapp.com.pem:extraCertChain=/srv/certs/private/star.fusionapp.com.pem',
        '--uri', 'https://196.8.131.140:8000',
        '--no-verify-tls',
        '--client-cert', '/srv/certs/private/sbvaf-fusion.pem',
        ]))
    run(' '.join([
        'docker', 'run',
        '--detach',
        '--restart=always',
        '--name', 'soapproxy-sbvaf-3',
        '--publish 8082:8082',
        '--volume=/srv/certs:/srv/certs:ro',
        'fusionapp/soapproxy',
        '--endpoint',
        'ssl:8082:privateKey=/srv/certs/private/star.fusionapp.com.pem:extraCertChain=/srv/certs/private/star.fusionapp.com.pem',
        '--uri', 'https://196.8.131.140:13203',
        '--no-verify-tls',
        ]))
    run(' '.join([
        'docker', 'run',
        '--detach',
        '--restart=always',
        '--name', 'soapproxy-sbvaf-4',
        '--publish 8083:8083',
        '--volume=/srv/certs:/srv/certs:ro',
        'fusionapp/soapproxy',
        '--endpoint',
        'ssl:8083:privateKey=/srv/certs/private/star.fusionapp.com.pem:extraCertChain=/srv/certs/private/star.fusionapp.com.pem',
        '--uri', 'https://mobilebanking.standardbank.co.za:9000',
        '--no-verify-tls',
        '--client-cert', '/srv/certs/private/sbvaf-fusion-prod.pem',
        ]))
    run(' '.join([
        'docker', 'run',
        '--detach',
        '--restart=always',
        '--name', 'soapproxy-sbvaf-5',
        '--publish 8084:8084',
        '--volume=/srv/certs:/srv/certs:ro',
        'fusionapp/soapproxy',
        '--endpoint',
        'ssl:8084:privateKey=/srv/certs/private/star.fusionapp.com.pem:extraCertChain=/srv/certs/private/star.fusionapp.com.pem',
        '--uri', 'https://196.8.110.17:21003',
        '--no-verify-tls',
        ]))
    run(' '.join([
        'docker', 'run',
        '--detach',
        '--restart=always',
        '--name', 'soapproxy-absa-1',
        '--publish 8085:8085',
        '--volume=/srv/certs:/srv/certs:ro',
        'fusionapp/soapproxy',
        '--endpoint',
        'ssl:8085:privateKey=/srv/certs/private/star.fusionapp.com.pem:extraCertChain=/srv/certs/private/star.fusionapp.com.pem',
        '--uri', 'https://e.absa.co.za',
        '--no-verify-tls',
        ]))
    run(' '.join([
        'docker', 'run',
        '--detach',
        '--restart=always',
        '--name', 'soapproxy-absa-2',
        '--publish 8086:8086',
        '--volume=/srv/certs:/srv/certs:ro',
        'fusionapp/soapproxy',
        '--endpoint',
        'ssl:8086:privateKey=/srv/certs/private/star.fusionapp.com.pem:extraCertChain=/srv/certs/private/star.fusionapp.com.pem',
        '--uri', 'https://eu.absa.co.za',
        '--no-verify-tls',
        ]))
