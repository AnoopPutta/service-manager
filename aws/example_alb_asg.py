from aws import launch_configuration as lc
from aws import alb
from aws import alb_listener
from aws import asg
from aws import alb_target_group


class ExampleElbAsg(object):

    def __init__(self, ts, aws_resource, input):
        self.aws_resource = aws_resource
        self.input_json = input
        self.ts = ts

    def add_instance(self):

        user_data = """#!/bin/bash
        cat > index.html <<EOF
        <h1>Hello, World</h1>
        EOF
        nohup busybox httpd -f -p "{{}}" &
        """

        server_port = 8080
        vpc_id = "vpc-74b24210"
        instance_type = "t2.micro"
        subnets = ['subnet-054c3ae2dd9d17e98', 'subnet-03ebea26038df39b3']
        name = "rakhs-test"
        tags = {"owner": "rakhs"}

        elb_sg = self.aws_resource.aws_security_group(
            name+"-elb", name='{}-elb'.format(name), vpc_id=vpc_id, tags=tags
        )

        elb_sg_ingress_rule = self.aws_resource.aws_security_group_rule(
            'allow_http_inbound', security_group_id=elb_sg.id,
            type='ingress', from_port=server_port, to_port=server_port,
            protocol='tcp', cidr_blocks=["0.0.0.0/0"])

        elb_sg_egress_rule = self.aws_resource.aws_security_group_rule(
            'allow_all_outbound', security_group_id=elb_sg.id,
            type='egress', from_port=0, to_port=0,
            protocol='-1', cidr_blocks=["0.0.0.0/0"])

        self.ts.add(elb_sg)
        self.ts.add(elb_sg_ingress_rule)
        self.ts.add(elb_sg_egress_rule)

        launch_config_sg = self.aws_resource.aws_security_group(
            name+"-inst", name='{}-instance'.format(name),
            vpc_id=vpc_id, tags=tags
        )

        launch_config_sg_egress_rule = self.aws_resource.aws_security_group_rule(
            'allow_lc_http_inbound', security_group_id=launch_config_sg.id,
            type='ingress', from_port=server_port, to_port=server_port,
            protocol='tcp', cidr_blocks=["0.0.0.0/0"])

        self.ts.add(launch_config_sg_egress_rule)
        self.ts.add(launch_config_sg)

        template_file = user_data.format(server_port)

        # input json for launch config
        self.input_json = {
            'name': name,
            "image_id":'ami-0b898040803850657',
            "instance_type": instance_type,
            "security_groups": [elb_sg.id],
            "user_data": template_file,
            "lifecycle": {
                'create_before_destroy': True
            }
        }
        launch_config = lc.LaunchConfiguration(
            self.aws_resource, self.input_json).add_instance()
        self.ts.add(launch_config)

        # input json for ALB
        self.input_json={
            "name": name,
            "security_groups": [elb_sg.id],
            "subnets": [
                "subnet-054c3ae2dd9d17e98",
                "subnet-03ebea26038df39b3"
            ],
            "tags": tags
        }

        application_lb = alb.ALB(self.aws_resource, self.input_json).add_instance()
        self.ts.add(application_lb)

        # input json for ALB Target Group
        self.input_json = {
            "name": name,
            "port": 8080,
            "protocol": "HTTP",
            "vpc_id": vpc_id
        }
        application_lb_target_group = alb_target_group.AlbTargetGroup(
            self.aws_resource, self.input_json).add_instance()
        self.ts.add(application_lb_target_group)

        # input json for ALB Listener
        self.input_json = {
            "name": name,
            "load_balancer_arn": application_lb.arn,
            "port": 8080,
            "protocol": "HTTP",
            "default_action": {
                "target_group_arn": application_lb_target_group.arn,
                "type": "forward"
            }
        }
        application_lb_listener = alb_listener.AlbListener(
            self.aws_resource, self.input_json).add_instance()
        self.ts.add(application_lb_listener)



        # input json for Autoscaling Group
        self.input_json = {
            "name": name,
            "launch_configuration": launch_config.id,
            "min_size": 2,
            "max_size": 3,
            "vpc_zone_identifier": subnets,
            "tag": [{
                'key': 'Name',
                'value': name,
                'propagate_at_launch': True
             }]
        }
        autoscaling_group= asg.AutoscalingGroup(self.aws_resource, self.input_json).add_instance()
        self.ts.add(autoscaling_group)

        # attach ALB target group to auto scaling group
        self.ts.add(self.aws_resource.aws_autoscaling_attachment(
            name, autoscaling_group_name=autoscaling_group.id,
            alb_target_group_arn=application_lb_target_group.arn)
        )
