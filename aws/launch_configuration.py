class LaunchConfiguration(object):

    def __init__(self, aws_resource, input):
        self.aws_resource = aws_resource
        self.input_json = input
        self.tags = {"owner": "rakhs"}

    def add_instance(self):
        """
            returns terraform launch configuration resource

            Parameters:
                self.json to contain
                name (string): name for resource
                image_id (string): AMI Image ID
                instance_type (string): instance type ex. t2.micro
                security_groups (list of strings): security group name/ids to attach
                user_data (string): user_data
                lifecycle (dict): lifecycle parameters

            Returns:
                returns terraform launch configuration resource
            """

        if "ebs_block_device" in self.input_json:
            return self.aws_resource.aws_launch_configuration(
                self.input_json["name"],
                image_id=self.input_json["image_id"],
                instance_type=self.input_json["instance_type"],
                security_groups=self.input_json["security_groups"],
                user_data=self.input_json["user_data"],
                lifecycle=self.input_json["lifecycle"],
                ebs_block_device=self.input_json.get("ebs_block_device", {}))
        else:
            return self.aws_resource.aws_launch_configuration(
                self.input_json["name"],
                image_id=self.input_json["image_id"],
                instance_type=self.input_json["instance_type"],
                security_groups=self.input_json["security_groups"],
                user_data=self.input_json["user_data"],
                lifecycle=self.input_json["lifecycle"]
            )
