from terraform.generator import Generator

tfgen = Generator('{"provider": "aws"}')
tfgen.generate_terraform()