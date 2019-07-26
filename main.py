from terraform.generator import Generator

tfgen = Generator('{"provider": "azure"}')
tfgen.generate_terraform()