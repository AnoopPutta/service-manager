from terrascript import output
from tls import private_key
from aws import launch_configuration as lc
from aws import alb
from aws import alb_listener
from aws import asg
from aws import alb_target_group
from aws import vpc
from aws import internet_gateway as igw
from aws import route_table
from aws import route
from aws import subnet
from aws import key_pair
from aws import db_subnet_group


class ExampleElbAsg(object):

    def __init__(self, ts, aws_resource, input):
        self.aws_resource = aws_resource
        self.input_json = input
        self.ts = ts

    def add_instance(self):

        owner = "test"
        stack = "test-stack"

        default_tags = {
            "Owner": owner,
            "Stack": stack
        }

        # input json for Key pair
        self.input_json = {
            "name": 'deployer'
        }
        deploy_key = private_key.PrivateKey(self.input_json).add_instance()
        self.ts.add(deploy_key)
        self.ts.add(output('public_key_pem', value=deploy_key.public_key_pem, description='The public key data in PEM format'))
        self.ts.add(output('private_key_pem ', value=deploy_key.private_key_pem , description='The private key data in PEM format'))

        self.input_json = {
            "name": 'deployer-key',
            "key_name": 'deployer-key',
            "public_key": deploy_key.public_key_openssh
        }
        key_pair_name = key_pair.KeyPair(self.aws_resource, self.input_json).add_instance()
        self.ts.add(key_pair_name)
        self.ts.add(output('key_pair_name ', value=key_pair_name.key_name , description='The key pair name'))

        # input json for VPC
        self.input_json = {
            "name": 'main',
            "cidr_block": '10.10.0.0/16',
            "tags": default_tags
        }
        main_vpc = vpc.Vpc(self.aws_resource, self.input_json).add_instance()
        self.ts.add(main_vpc)

        # input json for internet gateway
        self.input_json = {
            "name": 'public',
            "vpc_id": main_vpc.id,
            "tags": default_tags
        }
        public_igw = igw.InternetGateway(self.aws_resource, self.input_json).add_instance()
        self.ts.add(public_igw)

        # input json for public route table
        self.input_json = {
            "name": 'public',
            "vpc_id": main_vpc.id,
            "tags": default_tags
        }
        public_rtb = route_table.RouteTable(self.aws_resource, self.input_json).add_instance()
        self.ts.add(public_rtb)

        # input json for internet gateway route
        self.input_json = {
            "name": 'igw-route',
            "route_table_id": public_rtb.id,
            "destination_cidr_block": '0.0.0.0/0',
            "gateway_id": public_igw.id
        }
        igw_route = route.Route(self.aws_resource, self.input_json).add_instance()
        self.ts.add(public_rtb)

        public_subnet_cidrs = ['10.10.1.0/24', '10.10.2.0/24']
        private_subnet_cidrs = ['10.10.11.0/24', '10.10.12.0/24']
        availability_zones = ['us-east-1a', 'us-east-1b']

        public_subnets = []
        private_subnets = []
        for i in range(0, len(public_subnet_cidrs)):
            # input json for public subnets
            self.input_json = {
                "name": 'public_subnet_az'+str(i),
                "vpc_id": main_vpc.id,
                "cidr_block": public_subnet_cidrs[i],
                "availability_zone": availability_zones[i],
                "map_public_ip_on_launch": True,
                "tags": default_tags
            }
            public_subnet = subnet.Subnet(self.aws_resource, self.input_json).add_instance()
            self.ts.add(public_subnet)
            public_subnets.append(public_subnet)

        for i in range(0, len(private_subnet_cidrs)):
            # input json for public subnets
            self.input_json = {
                "name": 'private_subnet_az'+str(i),
                "vpc_id": main_vpc.id,
                "cidr_block": private_subnet_cidrs[i],
                "availability_zone": availability_zones[i],
                "map_public_ip_on_launch": False,
                "tags": self.input_json["tags"]
            }
            private_subnet = subnet.Subnet(self.aws_resource, self.input_json).add_instance()
            self.ts.add(private_subnet)
            private_subnets.append(private_subnet)

        # input json for rds db subnet group
        self.input_json = {
            "name": "rds",
            "subnet_ids": [
                private_subnets[0].id,
                private_subnets[1].id
            ],
            "tags": default_tags
        }
        rds_db_subnet_group = db_subnet_group.DBSubnetGroup(self.aws_resource, self.input_json).add_instance()
        self.ts.add(rds_db_subnet_group)
        self.ts.add(output('db_subnet_group_name', value=rds_db_subnet_group.id, description='The db subnet group name'))

        user_data = """#!/bin/bash
        cat > index.html <<EOF
        <h1>Hello, World</h1>
        EOF
        nohup busybox httpd -f -p "{{}}" &
        """

        server_port = 8080
        vpc_id = main_vpc.id
        instance_type = "t2.micro"
        subnets = [
            public_subnets[0].id,
            public_subnets[1].id
        ]
        name = stack

        elb_sg = self.aws_resource.aws_security_group(
            name+"-elb", name='{}-elb'.format(name), vpc_id=vpc_id, tags=default_tags
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
            vpc_id=vpc_id, tags=default_tags
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
            "subnets": subnets,
            "tags": default_tags
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

'''
{
  "output": {
    "db_subnet_group_name": {
      "description": "The db subnet group name",
      "value": "${aws_db_subnet_group.rds.id}"
    },
    "key_pair_name ": {
      "description": "The key pair name",
      "value": "${aws_key_pair.deployer-key.key_name}"
    },
    "private_key_pem ": {
      "description": "The private key data in PEM format",
      "value": "${tls_private_key.deployer.private_key_pem}"
    },
    "public_key_pem": {
      "description": "The public key data in PEM format",
      "value": "${tls_private_key.deployer.public_key_pem}"
    }
  },
  "provider": {
    "aws": {
      "__DEFAULT__": {
        "region": "us-east-1"
      }
    }
  },
  "resource": {
    "aws_alb": {
      "test-stack": {
        "name": "test-stack",
        "security_groups": [
          "${aws_security_group.test-stack-elb.id}"
        ],
        "subnets": [
          "${aws_subnet.public_subnet_az0.id}",
          "${aws_subnet.public_subnet_az1.id}"
        ],
        "tags": {
          "Owner": "test",
          "Stack": "test-stack"
        }
      }
    },
    "aws_alb_listener": {
      "test-stack": {
        "default_action": {
          "target_group_arn": "${aws_alb_target_group.test-stack.arn}",
          "type": "forward"
        },
        "load_balancer_arn": "${aws_alb.test-stack.arn}",
        "port": 8080,
        "protocol": "HTTP"
      }
    },
    "aws_alb_target_group": {
      "test-stack": {
        "name": "test-stack",
        "port": 8080,
        "protocol": "HTTP",
        "vpc_id": "${aws_vpc.main.id}"
      }
    },
    "aws_autoscaling_attachment": {
      "test-stack": {
        "alb_target_group_arn": "${aws_alb_target_group.test-stack.arn}",
        "autoscaling_group_name": "${aws_autoscaling_group.test-stack.id}"
      }
    },
    "aws_autoscaling_group": {
      "test-stack": {
        "launch_configuration": "${aws_launch_configuration.test-stack.id}",
        "max_size": 3,
        "min_size": 2,
        "tag": [
          {
            "key": "Name",
            "propagate_at_launch": true,
            "value": "test-stack"
          }
        ],
        "vpc_zone_identifier": [
          "${aws_subnet.public_subnet_az0.id}",
          "${aws_subnet.public_subnet_az1.id}"
        ]
      }
    },
    "aws_db_subnet_group": {
      "rds": {
        "description": "RDS db subnet group",
        "name": "rds",
        "subnet_ids": [
          "${aws_subnet.private_subnet_az0.id}",
          "${aws_subnet.private_subnet_az1.id}"
        ],
        "tags": {
          "Owner": "test",
          "Stack": "test-stack"
        }
      }
    },
    "aws_internet_gateway": {
      "public": {
        "lifecycle": {
          "create_before_destroy": true
        },
        "tags": {
          "Owner": "test",
          "Stack": "test-stack"
        },
        "vpc_id": "${aws_vpc.main.id}"
      }
    },
    "aws_key_pair": {
      "deployer-key": {
        "key_name": "deployer-key",
        "public_key": "${tls_private_key.deployer.public_key_openssh}"
      }
    },
    "aws_launch_configuration": {
      "test-stack": {
        "image_id": "ami-0b898040803850657",
        "instance_type": "t2.micro",
        "lifecycle": {
          "create_before_destroy": true
        },
        "security_groups": [
          "${aws_security_group.test-stack-elb.id}"
        ],
        "user_data": "#!/bin/bash\n        cat > index.html <<EOF\n        <h1>Hello, World</h1>\n        EOF\n        nohup busybox httpd -f -p \"{}\" &\n        "
      }
    },
    "aws_route_table": {
      "public": {
        "lifecycle": {
          "create_before_destroy": true
        },
        "tags": {
          "Owner": "test",
          "Stack": "test-stack"
        },
        "vpc_id": "${aws_vpc.main.id}"
      }
    },
    "aws_security_group": {
      "test-stack-elb": {
        "name": "test-stack-elb",
        "tags": {
          "Owner": "test",
          "Stack": "test-stack"
        },
        "vpc_id": "${aws_vpc.main.id}"
      },
      "test-stack-inst": {
        "name": "test-stack-instance",
        "tags": {
          "Owner": "test",
          "Stack": "test-stack"
        },
        "vpc_id": "${aws_vpc.main.id}"
      }
    },
    "aws_security_group_rule": {
      "allow_all_outbound": {
        "cidr_blocks": [
          "0.0.0.0/0"
        ],
        "from_port": 0,
        "protocol": "-1",
        "security_group_id": "${aws_security_group.test-stack-elb.id}",
        "to_port": 0,
        "type": "egress"
      },
      "allow_http_inbound": {
        "cidr_blocks": [
          "0.0.0.0/0"
        ],
        "from_port": 8080,
        "protocol": "tcp",
        "security_group_id": "${aws_security_group.test-stack-elb.id}",
        "to_port": 8080,
        "type": "ingress"
      },
      "allow_lc_http_inbound": {
        "cidr_blocks": [
          "0.0.0.0/0"
        ],
        "from_port": 8080,
        "protocol": "tcp",
        "security_group_id": "${aws_security_group.test-stack-inst.id}",
        "to_port": 8080,
        "type": "ingress"
      }
    },
    "aws_subnet": {
      "private_subnet_az0": {
        "availability_zone": "us-east-1a",
        "cidr_block": "10.10.11.0/24",
        "lifecycle": {
          "create_before_destroy": true
        },
        "map_public_ip_on_launch": false,
        "tags": {
          "Owner": "test",
          "Stack": "test-stack"
        },
        "vpc_id": "${aws_vpc.main.id}"
      },
      "private_subnet_az1": {
        "availability_zone": "us-east-1b",
        "cidr_block": "10.10.12.0/24",
        "lifecycle": {
          "create_before_destroy": true
        },
        "map_public_ip_on_launch": false,
        "tags": {
          "Owner": "test",
          "Stack": "test-stack"
        },
        "vpc_id": "${aws_vpc.main.id}"
      },
      "public_subnet_az0": {
        "availability_zone": "us-east-1a",
        "cidr_block": "10.10.1.0/24",
        "lifecycle": {
          "create_before_destroy": true
        },
        "map_public_ip_on_launch": true,
        "tags": {
          "Owner": "test",
          "Stack": "test-stack"
        },
        "vpc_id": "${aws_vpc.main.id}"
      },
      "public_subnet_az1": {
        "availability_zone": "us-east-1b",
        "cidr_block": "10.10.2.0/24",
        "lifecycle": {
          "create_before_destroy": true
        },
        "map_public_ip_on_launch": true,
        "tags": {
          "Owner": "test",
          "Stack": "test-stack"
        },
        "vpc_id": "${aws_vpc.main.id}"
      }
    },
    "aws_vpc": {
      "main": {
        "cidr_block": "10.10.0.0/16",
        "enable_dns_hostnames": true,
        "enable_dns_support": true,
        "lifecycle": {
          "create_before_destroy": true
        },
        "tags": {
          "Owner": "test",
          "Stack": "test-stack"
        }
      }
    },
    "tls_private_key": {
      "deployer": {
        "algorithm": "RSA",
        "rsa_bits": 4096
      }
    }
  }
}
'''