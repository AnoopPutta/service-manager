class S3BucketObject(object):

    def __init__(self, aws_resource, input):
        self.aws_resource = aws_resource
        self.input_json = input

    def add_instance(self):
        """
            Returns a terraform S3 bucket object resource
        """

        kwargs = {
            "key": self.input_json["key"],
            "bucket": self.input_json["bucket"],
            "content": self.input_json["content"],
            "lifecycle": {"create_before_destroy": True}
        }

        return self.aws_resource.aws_s3_bucket_object(
            self.input_json["name"], **kwargs
        )