import argparse
from ec2_instance import *
import json
import os


def get_config(user_data_path):
    with open(user_data_path, 'r') as f:
        configs = json.load(f)
    return configs


def run_instance(config, user_data):
    instance = Instance(config, user_data)
    instance_creation_response = instance.create()
    print(instance_creation_response)


def terminate_instance(config_path):
    instance_list = []
    configs = get_config(config_path)
    EC2 = boto3.client('ec2', region_name=configs['region'])
    response = EC2.describe_instances()
    #print(response["Reservations"])
    # Check existence of at least one instance
    if response["Reservations"] is not []:
        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                # [TO DO] use instance['Tags'] to delete specific instances
                #if instance is in running [or stopped state to add later]
                if instance['State']['Code'] == 16:
                    instance_list.append(instance['InstanceId'])
                    print(f"[INFO] Found '{instance['State']['Name']}' instance '{instance['InstanceId']}'")
        #print(instance_list)
        if instance_list is not []:
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
                        #[TO DO] if current state is terminated, exit(1)
                        return {"Instance ID": ec2_resp['TerminatingInstances'][0]['InstanceId'],
                                "CurrentState": ec2_resp['TerminatingInstances'][0]['CurrentState']
                        }
                    except ClientError as e:
                        print("Error: ", e)
                else:
                    print("[INFO] No instance has been removed")
                    exit(0)
            else:
                print("[INFO] Wrong instance number!!!")
                exit(1)
        else:
            print("[**INFO] No instance to remove")
            exit(0)
    else:
        print("[INFO] No instance to remove")
        exit(0)


def create_s3Bucket():
    """[TO DO]"""
    pass


if __name__ == "__main__":
    config_path = os.path.join(os.getcwd(), "configs")
    parser = argparse.ArgumentParser(description="AWS EC2 and S3")
    parser.add_argument("-c", "--config", default=os.path.join(config_path, "configs.json"), metavar="Config", type=str)
    parser.add_argument("-u", "--userdata", default=os.path.join(config_path, "user-data"), metavar="User Data", type=str)
    args = parser.parse_args()

    run_instance(args.config, args.userdata)
    #terminate_instance(args.config)
