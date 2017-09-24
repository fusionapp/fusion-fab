from fabric.api import env

from . import diamond, fusion, soapproxy, tools



env.roledefs = {
    'fusion-uat': ['root@scarlet.fusionapp.com'],
    'fusion-prod': ['root@onyx.fusionapp.com'],
    }



__all__ = ['fusion', 'diamond', 'tools', 'soapproxy']
