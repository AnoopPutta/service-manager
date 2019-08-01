class CloudFront(object):

    def __init__(self, aws_resource, input_json):
        self.aws_resource = aws_resource
        self.input_json = input_json

    def add_instance(self):
        """
                   Returns a terraform VPC resource
        """

        if self.input_json.get("domain_name") is None:
            return

        domain_name = self.input_json.get("domain_name")

        return self.aws_resource.aws_cloudfront_distribution(self.input_json.get("name"), enabled = True, comment = 'cloud front to front-end ALB', default_root_object = 'index.html', default_cache_behavior={
            'allowed_methods' : ['DELETE', 'GET', 'HEAD', 'OPTIONS', 'PATCH', 'POST', 'PUT'],
            'cached_methods' : ['GET', 'HEAD'],
            'target_origin_id': 'origin_id',
            'viewer_protocol_policy' : 'allow-all',
            'forwarded_values': {'query_string': False, 'headers': ['Origin'], 'cookies': {'forward': 'none'}}
            },  origin={'domain_name' : domain_name, 'origin_id' : 'origin_id', 'custom_origin_config' : { 'http_port' : 80,'origin_protocol_policy' : 'http-only', 'origin_ssl_protocols': ['TLSv1'], 'https_port': 443}
                        },
            viewer_certificate={'cloudfront_default_certificate' : True}, restrictions={'geo_restriction' : {'restriction_type' : 'none'}}

        )


'''

{
  "resource": {
    "aws_cloudfront_distribution": {
      "alb_cloudfront": {
        "comment": "cloud front to front-end ALB",
        "default_cache_behavior": {
          "allowed_methods": [
            "DELETE",
            "GET",
            "HEAD",
            "OPTIONS",
            "PATCH",
            "POST",
            "PUT"
          ],
          "cached_methods": [
            "GET",
            "HEAD"
          ],
          "forwarded_values": {
            "cookies": {
              "forward": "none"
            },
            "headers": [
              "Origin"
            ],
            "query_string": false
          },
          "target_origin_id": "origin_id",
          "viewer_protocol_policy": "allow-all"
        },
        "enabled": true,
        "default_root_object" : "index.html",
        "origin": {

          "domain_name": "rakhs-test-928524329.us-east-1.elb.amazonaws.com",
          "origin_id": "origin_id",
          "custom_origin_config" : {
            "http_port" : 80,
            "origin_protocol_policy" : "http-only",
            "origin_ssl_protocols": ["TLSv1"],
            "https_port": 443
          }
        },
        "restrictions" : {
          "geo_restriction" : {
            "restriction_type" : "none"
          }

        },
        "viewer_certificate" : {
            "cloudfront_default_certificate" : true
          }
      }
    }
  }
}




'''
