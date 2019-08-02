

class RdsInstance(object):

    def __init__(self, aws_resource, input):
        self.aws_resource = aws_resource
        self.input_json = input

    def add_instance(self):
        # Json parse and create an instance
        # Add an AWS EC2 instance (add() syntax).

        name = self.input_json.get("name")
        identifier = self.input_json.get("identifier")
        tags = self.input_json.get("tags")
        instance_type = self.input_json.get("instance_type")
        if instance_type is None:
            instance_type = 'db.t2.micro'
        vpc_security_group_ids = self.input_json.get("vpc_security_group_ids")
        subnet_grp_name = self.input_json.get("db_subnet_group_name")

        json = self.input_json
        inst = self.aws_resource.aws_db_instance(name, identifier=identifier, instance_class='db.t2.micro',storage_type='gp2',engine='oracle-se1', engine_version='11.2.0.4.v6'
                              , license_model = 'license-included',allocated_storage=10,username="oracle",password='password',db_subnet_group_name=subnet_grp_name,
                              port=1521,vpc_security_group_ids=vpc_security_group_ids,skip_final_snapshot=True,tags=tags)
        return inst
