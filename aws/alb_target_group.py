class AlbTargetGroup(object):

    def __init__(self, aws_resource, input):
        self.aws_resource = aws_resource
        self.input_json = input

    def add_instance(self):
        """
            Returns a terraform ALB resource
        """
        kwargs = {
            "name": self.input_json["name"],
            "port": self.input_json["port"],
            "protocol": self.input_json["protocol"],
            "vpc_id": self.input_json["vpc_id"]
      }

        return self.aws_resource.alb_target_group(self.input_json["name"],
                                                 **kwargs)
