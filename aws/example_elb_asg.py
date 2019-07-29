from aws import launch_configuration as lc
from aws import elb
from aws import asg


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

        elb_sg = self.aws_resource.security_group(
            name+"-elb", name='{}-elb'.format(name), vpc_id=vpc_id, tags=tags
        )

        elb_sg_ingress_rule = self.aws_resource.security_group_rule(
            'allow_http_inbound', security_group_id=elb_sg.id,
            type='ingress', from_port=server_port, to_port=server_port,
            protocol='tcp', cidr_blocks=["0.0.0.0/0"])

        elb_sg_egress_rule = self.aws_resource.security_group_rule(
            'allow_all_outbound', security_group_id=elb_sg.id,
            type='egress', from_port=0, to_port=0,
            protocol='-1', cidr_blocks=["0.0.0.0/0"])

        self.ts.add(elb_sg)
        self.ts.add(elb_sg_ingress_rule)
        self.ts.add(elb_sg_egress_rule)

        launch_config_sg = self.aws_resource.security_group(
            name+"-inst", name='{}-instance'.format(name),
            vpc_id=vpc_id, tags=tags
        )

        launch_config_sg_egress_rule = self.aws_resource.security_group_rule(
            'allow_lc_http_inbound', security_group_id=launch_config_sg.id,
            type='ingress', from_port=server_port, to_port=server_port,
            protocol='tcp', cidr_blocks=["0.0.0.0/0"])

        self.ts.add(launch_config_sg_egress_rule)
        self.ts.add(launch_config_sg)

        template_file = user_data.format(server_port)

        # input json for launch config
        self.input_json = {
            'name': name, "image_id":'ami-0b898040803850657',
            "instance_type": instance_type,
            "security_groups": [
                elb_sg.id],
            "user_data": template_file,
            "lifecycle": {
                'create_before_destroy': True
            }
        }
        launch_config = lc.LaunchConfiguration(
            self.aws_resource, self.input_json).add_instance()
        self.ts.add(launch_config)

        # input json for ELB
        self.input_json= {
            "name": name,
            "subnets": ['subnet-054c3ae2dd9d17e98', 'subnet-03ebea26038df39b3'],
            "security_groups": [elb_sg.id],
            "listener": [{
                'lb_port': 80,
                'lb_protocol': 'HTTP',
                'instance_port': server_port,
                'instance_protocol': 'HTTP'
            }],
            "health_check": [{
                'healthy_threshold': 2,
                'unhealthy_threshold': 2,
                'timeout': 3,
                'interval': 30,
                'target': 'HTTP:{}/'.format(server_port)
            }],
            "tags": tags
            }

        elastic_lb=elb.ELB(self.aws_resource, self.input_json).add_instance()
        self.ts.add(elastic_lb)

        # input json for Autoscaling Group
        self.input_json = {
            "name": name,
            "launch_configuration": launch_config.id,
            "health_check_type": "ELB",
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

        # attach load balancer to auto scaling group
        self.ts.add(self.aws_resource.autoscaling_attachment(
            name, autoscaling_group_name=autoscaling_group.id,
            elb=elastic_lb.id)
        )


'''
{
  "provider": {
    "aws": {
      "__DEFAULT__": {
        "region": "us-east-1"
      }
    }
  },
  "resource": {
    "aws_autoscaling_attachment": {
      "rakhs-test": {
        "autoscaling_group_name": "${aws_autoscaling_group.rakhs-test.id}",
        "elb": "${aws_elb.rakhs-test.id}"
      }
    },
    "aws_autoscaling_group": {
      "rakhs-test": {
        "health_check_type": "ELB",
        "launch_configuration": "${aws_launch_configuration.rakhs-test.id}",
        "max_size": 3,
        "min_size": 2,
        "tag": [
          {
            "key": "Name",
            "propagate_at_launch": true,
            "value": "rakhs-test"
          }
        ],
        "vpc_zone_identifier": [
          "subnet-054c3ae2dd9d17e98",
          "subnet-03ebea26038df39b3"
        ]
      }
    },
    "aws_elb": {
      "rakhs-test": {
        "health_check": [
          {
            "healthy_threshold": 2,
            "interval": 30,
            "target": "HTTP:8080/",
            "timeout": 3,
            "unhealthy_threshold": 2
          }
        ],
        "listener": [
          {
            "instance_port": 8080,
            "instance_protocol": "HTTP",
            "lb_port": 80,
            "lb_protocol": "HTTP"
          }
        ],
        "name": "rakhs-test",
        "security_groups": [
          "${aws_security_group.rakhs-test-elb.id}"
        ],
        "subnets": [
          "subnet-054c3ae2dd9d17e98",
          "subnet-03ebea26038df39b3"
        ],
        "tags": {
          "Name": "rakhs"
        }
      }
    },
    "aws_launch_configuration": {
      "rakhs-test": {
        "image_id": "ami-0b898040803850657",
        "instance_type": "t2.micro",
        "lifecycle": {
          "create_before_destroy": true
        },
        "security_groups": [
          "${aws_security_group.rakhs-test-elb.id}"
        ],
        "user_data": "#!/bin/bash\n        cat > index.html <<EOF\n        <h1>Hello, World</h1>\n        EOF\n        nohup busybox httpd -f -p \"{}\" &\n        "
      }
    },
    "aws_security_group": {
      "rakhs-test-elb": {
        "name": "rakhs-test-elb",
        "tags": {
          "owner": "rakhs"
        },
        "vpc_id": "vpc-74b24210"
      },
      "rakhs-test-inst": {
        "name": "rakhs-test-instance",
        "tags": {
          "owner": "rakhs"
        },
        "vpc_id": "vpc-74b24210"
      }
    },
    "aws_security_group_rule": {
      "allow_all_outbound": {
        "cidr_blocks": [
          "0.0.0.0/0"
        ],
        "from_port": 0,
        "protocol": "-1",
        "security_group_id": "${aws_security_group.rakhs-test-elb.id}",
        "to_port": 0,
        "type": "egress"
      },
      "allow_http_inbound": {
        "cidr_blocks": [
          "0.0.0.0/0"
        ],
        "from_port": 8080,
        "protocol": "tcp",
        "security_group_id": "${aws_security_group.rakhs-test-elb.id}",
        "to_port": 8080,
        "type": "ingress"
      },
      "allow_lc_http_inbound": {
        "cidr_blocks": [
          "0.0.0.0/0"
        ],
        "from_port": 8080,
        "protocol": "tcp",
        "security_group_id": "${aws_security_group.rakhs-test-inst.id}",
        "to_port": 8080,
        "type": "ingress"
      }
    }
  }
}
'''
