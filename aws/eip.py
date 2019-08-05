class Eip(object):

    def __init__(self, aws_resource, input):
        self.aws_resource = aws_resource
        self.input_json = input

    def add_instance(self):
        """
            Returns a terraform Eip resource
        """

        kwargs = {
            "vpc": True,
            "lifecycle": {"create_before_destroy": True}
        }

        return self.aws_resource.aws_eip(
            self.input_json["name"], **kwargs
        )