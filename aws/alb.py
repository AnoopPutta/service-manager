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
