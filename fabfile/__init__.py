from fabric.api import env

from . import (
    clj_documint, diamond, documint, drone, dynamo, fusion, fusion_index,
    registry, slack_better_bitbucket, soapproxy, tools)



env.roledefs = {
    'fusion-uat': ['root@scarlet.fusionapp.com'],
    'fusion-prod': ['root@onyx.fusionapp.com'],
    }



__all__ = [
    'fusion', 'documint', 'diamond', 'dynamo', 'tools', 'fusion_index',
    'registry', 'slack_better_bitbucket', 'soapproxy', 'drone', 'clj_documint']
