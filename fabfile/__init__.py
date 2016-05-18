from fabric.api import env

from . import (
    clj_documint, diamond, documint, fusion, fusion_index, soapproxy, tools)



env.roledefs = {
    'fusion-uat': ['root@scarlet.fusionapp.com'],
    'fusion-prod': ['root@onyx.fusionapp.com'],
    }



__all__ = [
    'fusion', 'documint', 'diamond', 'tools', 'fusion_index', 'soapproxy',
    'clj_documint']
