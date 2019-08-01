from terrascript.tls import r as tls

class PrivateKey(object):

    def __init__(self, input):
        self.tls = tls
        self.input_json = input

    def add_instance(self):
        """
            Returns a terraform TLS private key resource
        """

        kwargs = {
            "algorithm": 'RSA',
            "rsa_bits": 4096
        }

        return self.tls.private_key(
            self.input_json["name"], **kwargs
        )