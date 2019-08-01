from providers.provider_factory import ProviderFactory


class Generator(object):

    def __init__(self, json_input):
        self.json_input = json_input

    def generate_terraform(self):
        pf = ProviderFactory(self.json_input)
        pf1 = pf.get_provider()
        return pf1.generate_terraform()
