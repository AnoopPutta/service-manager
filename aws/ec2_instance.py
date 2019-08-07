class Ec2Instance(object):

    def __init__(self, aws_resource, input):
        self.aws_resource = aws_resource
        self.input_json = input

    def add_instance(self):
        """
            Returns a terraform EC2 resource
        """

        kwargs = {
            "ami": self.input_json["ami"],
            "subnet_id": self.input_json["subnet_id"],
            "instance_type": self.input_json["instance_type"],
            "key_name": self.input_json["key_name"],
            "user_data": self.input_json["user_data"],
            "tags": self.input_json["tags"],
            "vpc_security_group_ids": self.input_json["vpc_security_group_ids"]
        }

        if self.input_json.get("ebs_block_device"):
            kwargs["ebs_block_device"] = self.input_json["ebs_block_device"]

        return self.aws_resource.instance(self.input_json["name"], **kwargs)
