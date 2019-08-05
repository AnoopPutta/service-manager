from aws.cloud_front import CloudFront
from aws.rds import *
from terrascript import provider, terraform, backend
from aws.examples import elb_asg
from aws.examples import elb_asg_ebs
from aws.examples import alb_asg


def generate_terraform(ts, awsapi, json_input):
    ts += provider('aws',region='us-east-1')

    stack = json_input["stack"]
    s3_bucket = 'sm-state'
    json_input['bucket'] = s3_bucket
    s3_backend = backend('s3', bucket=s3_bucket, key=stack + '/terraform.state', region='us-east-1')
    tf = terraform(backend=s3_backend)
    ts.add(tf)

    #xyz= RdsInstance(awsapi, json_input).get_instance()
    #ts.add(xyz)
    #elb_asg.ExampleElbAsg(ts, awsapi, json_input).add_instance()
    #elb_asg_ebs.ExampleElbAsgEbs(ts, awsapi, json_input).add_instance()

    alb_asg.ExampleElbAsg(ts, awsapi, json_input).add_instance()
    return ts
