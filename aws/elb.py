class ELB(object):

    def __init__(self, aws_resource, input):
        self.aws_resource = aws_resource
        self.input_json = input

    def add_instance(self):
        """
            Returns a terraform ELB resource
        """

        return self.aws_resource.aws_elb(
            self.input_json["name"], name=self.input_json["name"],
            subnets=self.input_json["subnets"],
            security_groups=self.input_json["security_groups"],
            listener=self.input_json["listener"],
            health_check=self.input_json["health_check"],
            tags=self.input_json["tags"]
        )
