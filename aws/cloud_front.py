
class CloudFront(object):

    def __init__(self, awsapi, input):
        self.awsApi = awsapi
        self.input_json = input

    def get_instance(self):
        json = self.input_json
        inst = self.awsApi.aws_cloudfront_distribution("alb_cludfront", enabled = True, comment = "cloud front to front-end ALB", origin={
            'domain_name' : 'xyz.com', 'origin_id' : 'origin_id', 'default_root_object' : 'index.html'
       })
        return inst


