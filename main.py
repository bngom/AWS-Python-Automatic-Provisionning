import argparse
from ec2_instance import *
import json
import os


def run_instance(config, user_data):
    instance = Instance(config, user_data)
    instance_creation_response = instance.create()


def terminate_instance(config):
    instance = Instance(config)
    response = instance.terminate_instance()
    return response

def create_s3Bucket():
    """[TO DO]"""
    pass


if __name__ == "__main__":
    config_path = os.path.join(os.getcwd(), "configs")
    parser = argparse.ArgumentParser(description="AWS EC2 and S3")
    parser.add_argument("-c", "--config", default=os.path.join(config_path, "configs.json"), metavar="Config", type=str)
    parser.add_argument("-u", "--userdata", default=os.path.join(config_path, "user-data"), metavar="User Data", type=str)
    args = parser.parse_args()

    #run_instance(args.config, args.userdata)
    terminate_instance(args.config)
