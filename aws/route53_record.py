class Route53Record(object):

    def __init__(self, aws_resource, input):
        self.aws_resource = aws_resource
        self.input_json = input

    def add_instance(self):
        """
            Returns a terraform Route53 zone resource
        """

        kwargs = {
            "name": self.input_json["dns_name"],
            "zone_id": self.input_json["zone_id"],
            "type": "A",
            "ttl": "60",
            "records": self.input_json["records"],
            "lifecycle": {"create_before_destroy": True}
        }

        return self.aws_resource.aws_route53_record(
            self.input_json["name"], **kwargs
        )