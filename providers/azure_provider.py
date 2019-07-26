from terrascript.azure import r as azureapi
from providers.provider import BaseProvider


class AzureProvider(BaseProvider):

    def __init__(self, json_input):
        self.azureApi = azureapi
        super(AzureProvider,self).__init__(json_input)

    def generate_terraform(self):
        print("AZURE")
        print(str(self.input_json))
