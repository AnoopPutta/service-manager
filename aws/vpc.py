class Vpc(object):

    def __init__(self, aws_resource, input):
        self.aws_resource = aws_resource
        self.input_json = input

    def add_instance(self):
        """
            Returns a terraform VPC resource
        """

        kwargs = {
            "cidr_block": self.input_json["cidr_block"],
            "enable_dns_support": True,
            "enable_dns_hostnames": True,
            "lifecycle": {"create_before_destroy": True},
            "tags": self.input_json["tags"]
        }

        if self.input_json.get("enable_dns_support"):
            kwargs["enable_dns_support"]=self.input_json["enable_dns_support"]

        if self.input_json.get("enable_dns_hostnames"):
            kwargs["enable_dns_hostnames"]=self.input_json["enable_dns_hostnames"]

        return self.aws_resource.aws_vpc(
            self.input_json["name"], **kwargs
        )

    #def get_resource(self):
    #    json = self.input_json
    #    name = json.get('name', 'main')
    #    cidr_block = json.get('cidr_block', '10.0.0.0/16')
    #    enable_dns_support = json.get('enable_dns_support', True)
    #    enable_dns_hostnames = json.get('enable_dns_hostnames', True)
    #    tags = json.get('tags', None)
    #    vpc = self.awsApi.aws_vpc(name, cidr_block=cidr_block, enable_dns_support=enable_dns_support,
    #                               enable_dns_hostnames=enable_dns_hostnames, lifecycle={'create_before_destroy':True},
    #                               tags=tags)
    #    self.ts.add(vpc)
    #    return vpc