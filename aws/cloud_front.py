
class CloudFront(object):

    def __init__(self, awsapi, input):
        self.awsApi = awsapi
        self.input_json = input

    def get_instance(self):
        json = self.input_json
        inst = self.awsApi.cloudfront_distribution("name")
        return inst
