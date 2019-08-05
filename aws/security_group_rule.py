class SecurityGroupRule(object):

    def __init__(self, aws_resource, input):
        self.aws_resource = aws_resource
        self.input_json = input

    def add_instance(self):
        """
            Returns a terraform security group rule resource
        """

        kwargs = {
            "type": self.input_json["type"],
            "security_group_id": self.input_json["security_group_id"],
            "from_port": self.input_json["from_port"],
            "to_port": self.input_json["to_port"],
            "protocol": self.input_json["protocol"],
            "cidr_blocks": self.input_json["cidr_blocks"]
        }

        return self.aws_resource.aws_security_group_rule(
            self.input_json["name"], **kwargs
        )