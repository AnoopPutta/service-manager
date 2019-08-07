from terraform.generator import Generator

tfgen = Generator('{"provider": "aws", "region": "us-east-1", "stack": "test1-stack1", "owner": "test1"}')
tf_json = tfgen.generate_terraform()

# Write terraform json to file
out_file = open('main.tf.json', 'w+')
out_file.write(tf_json)
out_file.close()