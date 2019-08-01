class DBSubnetGroup(object):

    def __init__(self, aws_resource, input):
        self.aws_resource = aws_resource
        self.input_json = input

    def add_instance(self):
        """
            Returns a terraform Route resource
        """

        kwargs = {
            "name": self.input_json["name"],
            "description": 'RDS db subnet group',
            "subnet_ids": self.input_json["subnet_ids"],
            "tags": self.input_json["tags"]
        }

        return self.aws_resource.aws_db_subnet_group(
            self.input_json["name"], **kwargs
        )