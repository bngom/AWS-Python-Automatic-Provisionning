import boto3
from botocore.exceptions import ClientError
import json


class Instance:
    """
    Class to handle EC2 instance automatic provisioning.
    """

    def __init__(self, config_file_path, user_data_file_path=None):
        """
        :param config_file_path: path to a JSON config file containing the EC2 instance parameters
        :param user_data_file_path: path to user data script
        """
        self._config_file_path = config_file_path
        self._user_data_file_path = user_data_file_path

    def get_config(self):
        with open(self._config_file_path, 'r') as f:
            configs = json.load(f)
        return configs

    def get_user_data(self):
        with open(self._user_data_file_path, 'r') as f:
            user_data = f.read()
        return user_data

    def launch_instance(self, EC2, config, user_data):
        """
        :param EC2:
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
        input("You are going to deploy an EC2 instance. Press any key to continue...")

        # get the configuration for the EC2 instance
        configs = self.get_config()

        # get user data
        user_data = self.get_user_data()

        EC2 = boto3.client('ec2', region_name=configs['region'])
        result = self.launch_instance(EC2, configs, user_data)
        print(f"[INFO] Instance launched instance-id: '{result['InstanceID']}'")

    def terminate_instance(self):
        instance_list = []
        configs = self.get_config()
        EC2 = boto3.client('ec2', region_name=configs['region'])
        response = EC2.describe_instances()
        # Check existence of at least one instance
        instance_state_code = {"pending": 0, "running": 16, "shutting - down": 32, "terminated": 48, "stopping": 64, "stopped": 80}
        if len(response["Reservations"]) !=0:
            for reservation in response["Reservations"]:
                for instance in reservation["Instances"]:
                    # [TO DO] use instance['Tags'] to delete specific instances
                    # if instance is in running or stopped state
                    if instance['State']['Code'] in (instance_state_code["running"], instance_state_code["stopped"]):
                        instance_list.append(instance['InstanceId'])
                        print(f"[INFO] Found '{instance['State']['Name']}' instance '{instance['InstanceId']}'")
            # print(instance_list)
            if len(instance_list) != 0:
                instance_to_delete = input(f"[DELETE INSTANCE] Type in instance id to delete: ")
                if instance_to_delete in instance_list:
                    delete = input(f"[DELETE INSTANCE] '{instance_to_delete}' is running: terminating it[Y/n]")
                    if delete == "Y":
                        try:
                            ec2_resp = EC2.terminate_instances(
                                InstanceIds=[
                                    instance_to_delete,
                                ]
                            )
                            # [TO DO] if current state is terminated, exit(1)
                            return {"Instance ID": ec2_resp['TerminatingInstances'][0]['InstanceId'],
                                    "CurrentState": ec2_resp['TerminatingInstances'][0]['CurrentState']
                                    }
                        except ClientError as e:
                            print("Error: ", e)
                    else:
                        print("[INFO] No instance has been removed")
                        exit(0)
                else:
                    print("[INFO] Wrong instance id!!!")
                    exit(1)
            else:
                print("[INFO] To be removed instance should be in running or stopped state")
                exit(0)
        else:
            print("[INFO] No Reservation - No instance to remove")
            exit(0)
