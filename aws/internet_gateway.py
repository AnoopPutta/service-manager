class InternetGateway(object):

    def __init__(self, aws_resource, input):
        self.aws_resource = aws_resource
        self.input_json = input

    def add_instance(self):
        """
            Returns a terraform Internet Gateway resource
        """

        kwargs = {
            "vpc_id": self.input_json["vpc_id"],
            "lifecycle": {"create_before_destroy": True},
            "tags": self.input_json["tags"]
        }

        return self.aws_resource.aws_internet_gateway(
            self.input_json["name"], **kwargs
        )