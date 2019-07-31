class Route(object):

    def __init__(self, aws_resource, input):
        self.aws_resource = aws_resource
        self.input_json = input

    def add_instance(self):
        """
            Returns a terraform Route resource
        """

        kwargs = {
            "route_table_id": self.input_json["route_table_id"],
            "destination_cidr_block": self.input_json["destination_cidr_block"],
            "gateway_id": self.input_json["gateway_id"],
            "lifecycle": {"create_before_destroy": True}
        }

        return self.aws_resource.aws_route_table(
            self.input_json["name"], **kwargs
        )