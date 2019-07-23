from providers.provider import ProviderFactory

pf = ProviderFactory('{"provider": "aws"}')
pf1 = pf.get_provider()
pf1.generate_terraform()