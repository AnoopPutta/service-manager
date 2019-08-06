from terrascript import output
from terrascript.local.r import local_file
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
from aws import cloud_front as cf
from aws import route_table_association as rta
from aws import key_pair
from aws import db_subnet_group
from aws import rds
from aws import ebs_volume
from aws import ec2_instance
from aws import volume_attachment
from aws import eip
from aws import nat_gateway
from aws import security_group as sg
from aws import security_group_rule as sg_rule
from aws import s3_bucket_object

class ExampleElbAsg(object):
    def __init__(self, ts, aws_resource, input):
        self.aws_resource = aws_resource
        self.input_json = input
        self.ts = ts

    def add_instance(self):

        stack = self.input_json["stack"]
        bucket = self.input_json["bucket"]
        default_tags = {
            "Owner": self.input_json["owner"],
            "Stack": stack
        }

        # input json for Key pair
        self.input_json = {
            "name": 'deployer'
        }
        deploy_key = private_key.PrivateKey(self.input_json).add_instance()
        self.ts.add(deploy_key)

        # Upload public key to S3
        self.input_json = {
            "name": 'public_key_pem',
            "bucket": bucket,
            "key": stack + '/sitekey/public_key.pem',
            "content": deploy_key.public_key_pem
        }
        public_key_path = s3_bucket_object.S3BucketObject(self.aws_resource, self.input_json).add_instance()
        self.ts.add(public_key_path)
        self.ts.add(output('public_key_path', value='./sitekey/public_key.pem'))
        self.ts.add(local_file('public_key', filename='./sitekey/public_key.pem', content=deploy_key.public_key_pem))

        # Upload private key to S3
        self.input_json = {
            "name": 'private_key_pem',
            "bucket": bucket,
            "key": stack + '/sitekey/private_key.pem',
            "content": deploy_key.private_key_pem
        }
        private_key_path = s3_bucket_object.S3BucketObject(self.aws_resource, self.input_json).add_instance()
        self.ts.add(private_key_path)
        self.ts.add(output('private_key_path', value='./sitekey/private_key.pem'))
        self.ts.add(local_file('private_key', filename='./sitekey/private_key.pem', content=deploy_key.private_key_pem))

        self.input_json = {
            "name": 'deployer-key',
            "key_name": 'deployer-key',
            "public_key": deploy_key.public_key_openssh
        }
        key_pair_name = key_pair.KeyPair(self.aws_resource, self.input_json).add_instance()
        self.ts.add(key_pair_name)
        self.ts.add(output('key_pair_name ', value=key_pair_name.key_name, description='The key pair name'))

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

        # input json for private route table
        self.input_json = {
            "name": 'private',
            "vpc_id": main_vpc.id,
            "tags": default_tags
        }
        private_rtb = route_table.RouteTable(self.aws_resource, self.input_json).add_instance()
        self.ts.add(private_rtb)

        # input json for internet gateway route
        self.input_json = {
            "name": 'igw-route',
            "route_table_id": public_rtb.id,
            "destination_cidr_block": '0.0.0.0/0',
            "gateway_id": public_igw.id
        }
        igw_route = route.Route(self.aws_resource, self.input_json).add_instance()
        self.ts.add(igw_route)

        public_subnet_cidrs = ['10.10.1.0/24', '10.10.2.0/24']
        private_subnet_cidrs = ['10.10.11.0/24', '10.10.12.0/24']
        availability_zones = ['us-east-1a', 'us-east-1b']
        nat_cidrs = '10.10.0.32/28'

        public_subnets = []
        private_subnets = []
        for i in range(0, len(public_subnet_cidrs)):
            # input json for public subnets
            self.input_json = {
                "name": 'public_subnet_az' + str(i),
                "vpc_id": main_vpc.id,
                "cidr_block": public_subnet_cidrs[i],
                "availability_zone": availability_zones[i],
                "map_public_ip_on_launch": True,
                "tags": default_tags
            }
            public_subnet = subnet.Subnet(self.aws_resource, self.input_json).add_instance()
            self.ts.add(public_subnet)
            public_subnets.append(public_subnet)

            # input json for route table association
            self.input_json = {
                "name": 'public_subnet_az' + str(i) + '_rta',
                "subnet_id": public_subnet.id,
                "route_table_id": public_rtb.id
            }
            subnet_rta = rta.RouteTableAssociation(self.aws_resource, self.input_json).add_instance()
            self.ts.add(subnet_rta)

        for i in range(0, len(private_subnet_cidrs)):
            # input json for public subnets
            self.input_json = {
                "name": 'private_subnet_az' + str(i),
                "vpc_id": main_vpc.id,
                "cidr_block": private_subnet_cidrs[i],
                "availability_zone": availability_zones[i],
                "map_public_ip_on_launch": False,
                "tags": default_tags
            }
            private_subnet = subnet.Subnet(self.aws_resource, self.input_json).add_instance()
            self.ts.add(private_subnet)
            private_subnets.append(private_subnet)

            # input json for route table association
            self.input_json = {
                "name": 'private_subnet_az' + str(i) + '_rta',
                "subnet_id": private_subnet.id,
                "route_table_id": private_rtb.id
            }
            subnet_rta = rta.RouteTableAssociation(self.aws_resource, self.input_json).add_instance()
            self.ts.add(subnet_rta)

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
        self.ts.add(
            output('db_subnet_group_name', value=rds_db_subnet_group.id, description='The db subnet group name'))

        # EIP for nat
        self.input_json = {
            "name": "nat"
        }
        eip_nat = eip.Eip(self.aws_resource, self.input_json).add_instance()
        self.ts.add(eip_nat)

        # Subnet for nat
        self.input_json = {
            "name": 'nat_public_subnet',
            "vpc_id": main_vpc.id,
            "cidr_block": nat_cidrs,
            "availability_zone": availability_zones[0],
            "map_public_ip_on_launch": True,
            "tags": default_tags
        }
        nat_subnet = subnet.Subnet(self.aws_resource, self.input_json).add_instance()
        self.ts.add(nat_subnet)

        # input json for route table association
        self.input_json = {
            "name": 'nat_public_subnet_rta',
            "subnet_id": nat_subnet.id,
            "route_table_id": public_rtb.id
        }
        nat_subnet_rta = rta.RouteTableAssociation(self.aws_resource, self.input_json).add_instance()
        self.ts.add(nat_subnet_rta)

        # NAT gw
        self.input_json = {
            "name": "nat",
            "allocation_id": eip_nat.id,
            "subnet_id": nat_subnet.id
        }
        nat_gw = nat_gateway.NatGateway(self.aws_resource, self.input_json).add_instance()
        self.ts.add(nat_gw)

        # input json for nat gateway route
        self.input_json = {
            "name": 'nat-gw-route',
            "route_table_id": private_rtb.id,
            "destination_cidr_block": '0.0.0.0/0',
            "nat_gateway_id": nat_gw.id
        }
        nat_gw_route = route.Route(self.aws_resource, self.input_json).add_instance()
        self.ts.add(nat_gw_route)

        user_data = """
        #!/bin/bash
        yum install httpd -y
        service httpd start
        chkconfig httpd on

        cat >/var/www/html/index.html <<EOL
        <html><body>My first EC2 instance</body></html>
        EOL
        """

        server_port = 80
        vpc_id = main_vpc.id
        instance_type = "t2.micro"
        image_id = "ami-0b898040803850657"
        subnets = [
            public_subnets[0].id,
            public_subnets[1].id
        ]
        name = stack
        ebs_size = 1
        ebs_volume_type = "standard"
        ebs_volume_dev_id = "/dev/sda2"


        # Default Security group for Load Balancers and ASG
        self.input_json = {
            "name": 'elb-asg',
            "vpc_id": main_vpc.id,
            "description": "Default lb sg",
            "tags": default_tags
        }
        default_sg = sg.SecurityGroup(self.aws_resource, self.input_json).add_instance()
        self.ts.add(default_sg)

        self.input_json = {
            "name": 'allow_http_inbound',
            "type": 'ingress',
            "security_group_id": default_sg.id,
            "from_port": server_port,
            "to_port": server_port,
            "protocol": 'tcp',
            "cidr_blocks": ["0.0.0.0/0"]
        }
        default_sg_ingress_rule = sg_rule.SecurityGroupRule(self.aws_resource, self.input_json).add_instance()
        self.ts.add(default_sg_ingress_rule)

        self.input_json = {
            "name": 'allow_ssh_inbound',
            "type": 'ingress',
            "security_group_id": default_sg.id,
            "from_port": 22,
            "to_port": 22,
            "protocol": 'tcp',
            "cidr_blocks": ["0.0.0.0/0"]
        }
        ssh_sg_ingress_rule = sg_rule.SecurityGroupRule(self.aws_resource, self.input_json).add_instance()
        self.ts.add(ssh_sg_ingress_rule)

        self.input_json = {
            "name": 'allow_all_outbound',
            "type": 'egress',
            "security_group_id": default_sg.id,
            "from_port": 0,
            "to_port": 0,
            "protocol": '-1',
            "cidr_blocks": ["0.0.0.0/0"]
        }
        default_sg_egress_rule = sg_rule.SecurityGroupRule(self.aws_resource, self.input_json).add_instance()
        self.ts.add(default_sg_egress_rule)

        #################################### OHS Start #################################
        # OHS: Input json for ALB
        self.input_json = {
            "name": name,
            "security_groups": [default_sg.id],
            "subnets": subnets,
            "tags": default_tags
        }

        application_lb = alb.ALB(self.aws_resource, self.input_json).add_instance()
        self.ts.add(application_lb)

        # OHS: Input json for ALB Target Group
        self.input_json = {
            "name": name,
            "port": server_port,
            "protocol": "HTTP",
            "vpc_id": vpc_id
        }
        application_lb_target_group = alb_target_group.AlbTargetGroup(
            self.aws_resource, self.input_json).add_instance()
        self.ts.add(application_lb_target_group)

        # OHS: Input json for ALB Listener
        self.input_json = {
            "name": name,
            "load_balancer_arn": application_lb.arn,
            "port": server_port,
            "protocol": "HTTP",
            "default_action": {
                "target_group_arn": application_lb_target_group.arn,
                "type": "forward"
            }
        }
        application_lb_listener = alb_listener.AlbListener(
            self.aws_resource, self.input_json).add_instance()
        self.ts.add(application_lb_listener)

        # OHS: Input json for launch config
        self.input_json = {
            'name': name,
            "image_id": image_id,
            "instance_type": instance_type,
            "security_groups": [default_sg.id],
            "user_data": user_data,
            "lifecycle": {
                'create_before_destroy': True
            },
            "key_name": key_pair_name.key_name
        }
        launch_config = lc.LaunchConfiguration(
            self.aws_resource, self.input_json).add_instance()
        self.ts.add(launch_config)

        # OHS: Input json for ALB Autoscaling Group
        self.input_json = {
            "name": name,
            "launch_configuration": launch_config.id,
            "min_size": 2,
            "max_size": 2,
            "vpc_zone_identifier": subnets,
            "tag": [{
                'key': 'Name',
                'value': name,
                'propagate_at_launch': True
            }]
        }
        autoscaling_group = asg.AutoscalingGroup(self.aws_resource, self.input_json).add_instance()
        self.ts.add(autoscaling_group)

        # OHS: Attach ALB target group to auto scaling group
        self.ts.add(self.aws_resource.aws_autoscaling_attachment(
            name, autoscaling_group_name=autoscaling_group.id,
            alb_target_group_arn=application_lb_target_group.arn)
        )

        #################################### OAM Start #################################
        #Zone1
        i = 1
        for s in private_subnets:
            self.input_json = {
                "name": name+str(i),
                "availability_zone": availability_zones[i-1], # availablity zone 1, TODO: improve this
                "size": ebs_size,
                "type": ebs_volume_type,
                "tags": default_tags
            }
            ebs_vol = ebs_volume.EbsVolume(self.aws_resource, self.input_json).add_instance()
            self.ts.add(ebs_vol)

            self.input_json = {
                "name": name+'-'+str(i)+'-private',
                "ami": image_id,
                "subnet_id": s.id,
                "instance_type": instance_type,
                "key_name": key_pair_name.key_name,
                "user_data": user_data,
                "security_groups": [default_sg.id],
                "tags": default_tags
            }
            inst = ec2_instance.Ec2Instance(self.aws_resource, self.input_json).add_instance()
            self.ts.add(inst)

            self.input_json = {
                "name": name+str(i),
                "volume_id": ebs_vol.id,
                "instance_id": inst.id,
                "device_name": ebs_volume_dev_id
            }
            self.ts.add(volume_attachment.VolumeAttachment(self.aws_resource, self.input_json).add_instance())
            i += 1
        '''
        # input_json for CloudFront
        self.input_json = {
            "name": name + '_cloud_front',
            "domain_name": application_lb.dns_name

        }
        cloud_front = cf.CloudFront(self.aws_resource, self.input_json).add_instance()
        self.ts.add(cloud_front)
        self.ts.add(
            output('cloud_front_endpoint', value=cloud_front.domain_name, description='CloudFroint end-point'))

        # input_json for RDS
        self.input_json = {
            "name": name + '_rds',
            "identifier": "testid",
            "tags": default_tags,
            "vpc_security_group_ids" : [main_vpc.default_security_group_id],
            "db_subnet_group_name": rds_db_subnet_group.id
        }

        rds_instance = rds.RdsInstance(self.aws_resource, self.input_json).add_instance()
        self.ts.add(rds_instance)
        self.ts.add(
            output('rds_endpoint', value=rds_instance.address, description='RDS end-point'))
        '''