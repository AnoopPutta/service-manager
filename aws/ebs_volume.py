class EbsVolume(object):

    def __init__(self, aws_resource, input):
        self.aws_resource = aws_resource
        self.input_json = input

    def add_instance(self):
        """
            Returns a terraform EBS volume resource
        """

        kwargs = {
            "availability_zone": self.input_json["availability_zone"],
            "size": self.input_json["size"],
            "type": self.input_json["type"],
            "tags": self.input_json["tags"]
        }

        return self.aws_resource.ebs_volume(self.input_json["name"], **kwargs)
