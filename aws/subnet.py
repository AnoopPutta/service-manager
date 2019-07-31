class Subnet(object):

    def __init__(self, aws_resource, input):
        self.aws_resource = aws_resource
        self.input_json = input

    def add_instance(self):
        """
            Returns a terraform Subnet resource
        """

        kwargs = {
            "vpc_id": self.input_json["vpc_id"],
            "cidr_block": self.input_json["cidr_block"],
            "availability_zone": self.input_json["availability_zone"],
            "map_public_ip_on_launch": self.input_json['map_public_ip_on_launch'],
            "lifecycle": {"create_before_destroy": True},
            "tags": self.input_json["tags"]
        }

        return self.aws_resource.aws_subnet(
            self.input_json["name"], **kwargs
        )

    #def get_resource(self):
    #    json = self.input_json
    #    vpc_id = json.get('vpc_id', None)
    #    cidr_block = json.get('cidr_block', '10.0.0.0/24')
    #    availability_zone = json.get('availability_zone', None)
    #    subnet_type = json.get('subnet_type', 'private')
    #    name = json.get('name', subnet_type)
    #    tags = json.get('tags', None)

    #    subnet_type = variable('subnet_type', default=subnet_type)
    #    public_ip_required = variable('public_ip_required', default={'public': 'true', 'private': 'false'})
    #    subnet = self.awsApi.aws_subnet(name, vpc_id=vpc_id, cidr_block=cidr_block, availability_zone=availability_zone,
    #                                    map_public_ip_on_launch=function.lookup(public_ip_required, subnet_type),
    #                                    lifecycle={'create_before_destroy': True}, tags=tags)

    #    self.ts.add(subnet)
    #    self.ts.add(subnet_type)
    #    self.ts.add(public_ip_required)
    #    return subnet