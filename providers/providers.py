import json
from terrascript import Terrascript, provider
from terrascript.aws import r as awsapi
from terrascript.azure import r as azureapi
import aws.generator


class BaseProvider(object):

    def __init__(self, json_input):
        self.input_json = json_input
        self.ts = Terrascript()

    def generate_terraform(self):
        raise NotImplementedError()


class AwsProvider(BaseProvider):

    def __init__(self, json_input):
        self.awsApi = awsapi
        super(AwsProvider,self).__init__(json_input)

    def generate_terraform(self):
        aws.generator.generate_terraform(self.ts,self.awsApi, self.input_json )
        print(self.ts.dump())


class AzureProvider(BaseProvider):

    def __init__(self, json_input):
        self.azureApi = azureapi
        super(AzureProvider,self).__init__(json_input)

    def generate_terraform(self):
        print("AZURE")
        print(str(self.input_json))


class ProviderFactory(object):
    _provider_type = None

    def __init__(self, json_input):

        json_data = json.loads(json_input)
        self._provider_type = json_data.get("provider", None)
        self.json_input = json_data

    def get_provider(self):

        if self._provider_type == "aws":
            return AwsProvider(self.json_input)
        if self._provider_type == "azure":
            return AzureProvider(self.json_input)