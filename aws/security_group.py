class SecurityGroup(object):

    def __init__(self, aws_resource, input):
        self.aws_resource = aws_resource
        self.input_json = input

    def add_instance(self):
        """
            Returns a terraform security group resource
        """

        kwargs = {
            "vpc_id": self.input_json["vpc_id"],
            "name": self.input_json["name"],
            "description": self.input_json["description"],
            "lifecycle": {"create_before_destroy": True},
            "tags": self.input_json["tags"]
        }

        return self.aws_resource.aws_security_group(
            self.input_json["name"], **kwargs
        )