import boto3
from botocore.exceptions import ClientError
import json


class Instance:
    """
    Class to handle EC2 instance automatic provisioning.
    """
    def __init__(self, config_file_path, user_data_file_path):
        """
        :param config_file_path: path to a JSON config file containing the EC2 instance parameters
        :param user_data_file_path: path to user data script
        """
        self._config_file_path = config_file_path
        self._user_data_file_path = user_data_file_path

    def launch_instance(self, EC2, config, user_data):
        """
        :param EC2: An instance of the class
        :param config: configuration data for the EC2 instance
        :param user_data: user data script to execute at launch
        :return: a dictionary with the id of the instance created...
        """
        tag_specs = [{}]
        tag_specs[0]['ResourceType'] = 'instance'
        tag_specs[0]['Tags'] = config['set_new_instance_tags']
        try:
            ec2_response = EC2.run_instances(
                ImageId=config['ami'],
                InstanceType=config['instance_type'],
                KeyName=config['ssh_key_name'],
                MinCount=1,
                MaxCount=1,
                SecurityGroupIds=config['security_group_ids'],
                TagSpecifications=tag_specs,
                UserData=user_data
            )
            print("executing user data...\n", user_data)

            new_instance_resp = ec2_response['Instances'][0]
            instance_id = new_instance_resp['InstanceId']
        except ClientError as e:
            print('Error:', e)

        return {
                    "InstanceID": instance_id,
                    "EC2Response": new_instance_resp
        }

    def create(self):
        """
        Set the context and Trigger an instance creation.
        """
        input("You are going to deploy an Jupiter Notebook on a EC2 instance. Press any key to continue...")
        # get the configuration for the EC2 instance

        with open(self._config_file_path, 'r') as f:
            configs = json.load(f)

        # get user data
        with open(self._user_data_file_path, 'r') as f:
            user_data = f.read()

        EC2 = boto3.client('ec2', region_name=configs['region'])
        result = self.launch_instance(EC2, configs, user_data)
        print(f"[INFO] Instance launched instance-id: '{result['InstanceID']}'")
