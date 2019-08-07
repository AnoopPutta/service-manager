class Route53Zone(object):

    def __init__(self, aws_resource, input):
        self.aws_resource = aws_resource
        self.input_json = input

    def add_instance(self):
        """
            Returns a terraform Route53 zone resource
        """

        kwargs = {
            "name": self.input_json["domain_name"],
            "vpc": {

                "vpc_id": self.input_json["vpc_id"],
                "vpc_region": self.input_json["vpc_region"],
            },
            "lifecycle": {"create_before_destroy": True},
            "tags": self.input_json["tags"]
        }

        return self.aws_resource.aws_route53_zone(
            self.input_json["name"], **kwargs
        )