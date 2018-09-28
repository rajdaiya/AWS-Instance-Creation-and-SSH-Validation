import boto.ec2
import boto3
from botocore.exceptions import ClientError
import botocore
import time

'''
Create a connection. Specify the region where you want to
setup ec2 along with your security credentials
'''
conn = boto.ec2.connect_to_region("us-east-2",
		aws_access_key_id = '#########',
		aws_secret_access_key = '##########')

'''
Launch your ec2 instance. This requires ami image id and instance type.
Refer to the AWS documentation for details. You need to setup your
key-pair and security group before launching.

'''

''' Creating key pair '''

ec2 = boto3.resource('ec2')

try:
	outfile = open('keypair.pem','w')
	key_pair = ec2.create_key_pair(KeyName='keypair')
	KeyPairOut = str(key_pair.key_material)
	outfile.write(KeyPairOut)
except ClientError as e:
    print( "Key Pair Already Exist")


''' Creating Security Group '''

ec2 = boto3.client('ec2')

response = ec2.describe_vpcs()
vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')

try:
    response = ec2.create_security_group(GroupName='SECURITYGROUP',
                                         Description='security group for ec2 instance',
                                         VpcId=vpc_id)
    security_group_id = response['GroupId']
    print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))

    data = ec2.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {'IpProtocol': 'tcp',
             'FromPort': 80,
             'ToPort': 80,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp',
             'FromPort': 22,
             'ToPort': 22,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
        ])
except ClientError as e:
    print("Security Group Already Exist")

''' Running the ec2 instance '''

'''conn.run_instances(
        'ami-0b59bfac6be064b78',
        key_name = 'keypair',
        instance_type = 't2.micro',
        security_groups = ['SECURITYGROUP']
		)'''


''' Listing Instance ID and Public IP for the ec2 Instance '''

ec2 = boto3.resource('ec2')

# Get information for all running instances
instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running', 'pending']}])

for instance in instances:
	print("Instance ID  and Public IP :" + " " + instance.id + " " + instance.public_ip_address)

''' List Instance Region '''
my_session = boto3.session.Session()
my_region = my_session.region_name

print("Region for ec2 Instance : " + my_region)


'''
Stop instance
'''
running_instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])


for instance in running_instances:
	conn.stop_instances(instance_ids=[instance.id])


'''
Terminate instance
'''
stopped_instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}])

for instance in stopped_instances:
	conn.terminate_instances(instance_ids=[instance.id])

