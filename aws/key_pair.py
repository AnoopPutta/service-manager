class KeyPair(object):

    def __init__(self, aws_resource, input):
        self.aws_resource = aws_resource
        self.input_json = input

    def add_instance(self):
        """
            Returns a terraform Key pair resource
        """

        kwargs = {
            "key_name": self.input_json["key_name"],
            "public_key": self.input_json["public_key"]
        }

        return self.aws_resource.aws_key_pair(
            self.input_json["name"], **kwargs
        )