class ALB(object):

    def __init__(self, aws_resource, input):
        self.aws_resource = aws_resource
        self.input_json = input

    def add_instance(self):
        """
            Returns a terraform ALB resource
        """
        kwargs = {
            "name": self.input_json["name"],
            "subnets": self.input_json["subnets"],
            "security_groups": self.input_json["security_groups"],
            "tags": self.input_json["tags"]
        }

        return self.aws_resource.aws_alb(
            self.input_json["name"], **kwargs
        )


# {
#   "resource": {
#     "aws_autoscaling_group": {
#       "rakhs-test": {
#         "launch_configuration": "${aws_launch_configuration.rakhs-test.id}",
#         "max_size": 3,
#         "min_size": 2,
#         "tag": [
#           {
#             "key": "Name",
#             "propagate_at_launch": true,
#             "value": "rakhs-test"
#           }
#         ],
#         "vpc_zone_identifier": [
#           "subnet-054c3ae2dd9d17e98",
#           "subnet-03ebea26038df39b3"
#         ]
#       }
#     },
#     "aws_alb": {
#       "rakhs-test": {
#         "name": "rakhs-test",
#         "security_groups": [
#           "${aws_security_group.rakhs-test-elb.id}"
#         ],
#         "subnets": [
#           "subnet-054c3ae2dd9d17e98",
#           "subnet-03ebea26038df39b3"
#         ]
#       }
#     },
#     "aws_alb_listener": {
#       "rakhs-test": {
#         "load_balancer_arn": "${aws_alb.rakhs-test.arn}",
#         "port": 8080,
#         "protocol": "HTTP",
#         "default_action": {
#           "target_group_arn": "${aws_alb_target_group.rakhs-test.id}",
#           "type": "forward"
#         }
#       }
#     },
#     "aws_alb_target_group": {
#       "rakhs-test": {
#         "name": "rakhs-test",
#         "port": 8080,
#         "protocol": "HTTP",
#         "vpc_id": "vpc-74b24210"
#       }
#     },
#     "aws_autoscaling_attachment": {
#       "rakhs-test": {
#         "alb_target_group_arn": "${aws_alb_target_group.rakhs-test.arn}",
#         "autoscaling_group_name": "${aws_autoscaling_group.rakhs-test.id}"
#       }
#     },
#     "aws_launch_configuration": {
#       "rakhs-test": {
#         "image_id": "ami-0b898040803850657",
#         "instance_type": "t2.micro",
#         "lifecycle": {
#           "create_before_destroy": true
#         },
#         "security_groups": [
#           "${aws_security_group.rakhs-test-elb.id}"
#         ],
#         "user_data": "#!/bin/bash\n        cat > index.html <<EOF\n        <h1>Hello, World</h1>\n        EOF\n        nohup busybox httpd -f -p \"{}\" &\n        "
#       }
#     },
#     "aws_security_group": {
#       "rakhs-test-elb": {
#         "name": "rakhs-test-elb",
#         "vpc_id": "vpc-74b24210"
#       },
#       "rakhs-test-inst": {
#         "name": "rakhs-test-instance",
#         "vpc_id": "vpc-74b24210"
#       }
#     },
#     "aws_security_group_rule": {
#       "allow_all_outbound": {
#         "cidr_blocks": [
#           "0.0.0.0/0"
#         ],
#         "from_port": 0,
#         "protocol": "-1",
#         "security_group_id": "${aws_security_group.rakhs-test-elb.id}",
#         "to_port": 0,
#         "type": "egress"
#       },
#       "allow_http_inbound": {
#         "cidr_blocks": [
#           "0.0.0.0/0"
#         ],
#         "from_port": 8080,
#         "protocol": "tcp",
#         "security_group_id": "${aws_security_group.rakhs-test-elb.id}",
#         "to_port": 8080,
#         "type": "ingress"
#       },
#       "allow_server_http_inbound": {
#         "cidr_blocks": [
#           "0.0.0.0/0"
#         ],
#         "from_port": 8080,
#         "protocol": "tcp",
#         "security_group_id": "${aws_security_group.rakhs-test-inst.id}",
#         "to_port": 8080,
#         "type": "ingress"
#       }
#     }
#   }
# }