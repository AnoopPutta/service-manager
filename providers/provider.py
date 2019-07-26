from terrascript import Terrascript, provider


class BaseProvider(object):

    def __init__(self, json_input):
        self.input_json = json_input
        self.ts = Terrascript()

    def generate_terraform(self):
        raise NotImplementedError()






