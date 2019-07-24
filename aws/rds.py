

class RdsInstance(object):

    def __init__(self, awsApi, input):
        self.awsApi = awsApi
        self.input_json = input

    def get_instance(self):
        # Json parse and create an instance
        # Add an AWS EC2 instance (add() syntax).
        json = self.input_json
        inst = self.awsApi.aws_db_instance('MYDB', identifier='demo-db', instance_class='db.t2.micro',storage_type='gp2',engine='oracle-se1', engine_version='11.2.0.4.v6'
                              , license_model = 'license-included',allocated_storage=10,username="oracle",password='password',db_subnet_group_name='db-subnet',
                              port=1521,security_group_names='default',tags={
                                      'stack': 'test',
                                      'env': 'dev'

                                  })
        return inst
