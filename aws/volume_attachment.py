class VolumeAttachment(object):

    def __init__(self, aws_resource, input):
        self.aws_resource = aws_resource
        self.input_json = input

    def add_instance(self):
        """
            Returns a terraform volume attachment resource
        """

        kwargs = {
            "device_name": self.input_json["device_name"],
            "volume_id": self.input_json["volume_id"],
            "instance_id": self.input_json["instance_id"]
        }

        return self.aws_resource.volume_attachment(self.input_json["name"], **kwargs)
