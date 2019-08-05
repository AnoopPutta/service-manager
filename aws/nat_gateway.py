class NatGateway(object):

    def __init__(self, aws_resource, input):
        self.aws_resource = aws_resource
        self.input_json = input

    def add_instance(self):
        """
            Returns a terraform NAT gw resource
        """

        kwargs = {
            "allocation_id": self.input_json["allocation_id"],
            "subnet_id": self.input_json["subnet_id"],
            "lifecycle": {"create_before_destroy": True}
        }

        return self.aws_resource.aws_nat_gateway(
            self.input_json["name"], **kwargs
        )