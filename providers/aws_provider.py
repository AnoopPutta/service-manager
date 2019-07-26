from terrascript.aws import r as awsapi
from providers.provider import BaseProvider
import aws.generator


class AwsProvider(BaseProvider):

    def __init__(self, json_input):
        self.awsApi = awsapi
        super(AwsProvider,self).__init__(json_input)

    def generate_terraform(self):
        aws.generator.generate_terraform(self.ts,self.awsApi, self.input_json )
        print(self.ts.dump())
