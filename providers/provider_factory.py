from providers.aws_provider import *
from providers.azure_provider import *
import json

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