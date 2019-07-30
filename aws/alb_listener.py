class AlbListener(object):

    def __init__(self, aws_resource, input):
        self.aws_resource = aws_resource
        self.input_json = input

    def add_instance(self):
        """
            Returns a terraform ALB resource
        """
        kwargs = {
            "load_balancer_arn": self.input_json["load_balancer_arn"],
            "port": self.input_json["port"],
            "protocol": self.input_json["protocol"],
            "default_action": self.input_json["default_action"]
        }

        return self.aws_resource.alb_listener(self.input_json["name"], **kwargs)
