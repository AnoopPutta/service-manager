from aws.cloud_front import CloudFront
from aws.rds import *
from terrascript import provider


def generate_terraform(ts, awsapi, json_input):
    ts += provider('aws',region='us-east-1')
    xyz= CloudFront(awsapi, json_input).get_instance()
    ts.add(xyz)
    return ts