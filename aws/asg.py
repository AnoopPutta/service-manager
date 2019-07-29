class AutoscalingGroup(object):

    def __init__(self, aws_resource, input):
        self.aws_resource = aws_resource
        self.input_json = input

    def add_instance(self):
        """
            Returns a terraform ASG resource
        """

        return self.aws_resource.aws_autoscaling_group(self.input_json["name"],
                              launch_configuration=self.input_json["launch_configuration"],
                              health_check_type=self.input_json["health_check_type"],
                              min_size=self.input_json["min_size"],
                              max_size=self.input_json["max_size"],
                              vpc_zone_identifier=self.input_json["vpc_zone_identifier"],
                                tag=self.input_json["tag"])
