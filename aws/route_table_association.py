class RouteTableAssociation(object):

    def __init__(self, aws_resource, input):
        self.aws_resource = aws_resource
        self.input_json = input

    def add_instance(self):
        """
            Returns a terraform Route Table resource
        """

        kwargs = {
            "subnet_id": self.input_json["subnet_id"],
            "route_table_id": self.input_json["route_table_id"]
        }

        return self.aws_resource.aws_route_table_association(
            self.input_json["name"], **kwargs
        )