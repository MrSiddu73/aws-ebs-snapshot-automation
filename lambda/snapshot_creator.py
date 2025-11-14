import boto3
import os

sns = boto3.client('sns')
SNS_ARN = os.environ.get("SNS_TOPIC_ARN")

def notify_success(msg):
    sns.publish(
        TopicArn=SNS_ARN,
        Subject="Snapshot Success",
        Message=msg
    )

def notify_error(msg):
    sns.publish(
        TopicArn=SNS_ARN,
        Subject="Snapshot Error",
        Message=msg
    )

def lambda_handler(event, context):
    regions = []

    ec2_client = boto3.client('ec2')
    regions_response = ec2_client.describe_regions()

    for region in regions_response['Regions']:
        regions.append(region['RegionName'])

    snapshots_created = []

    for region in regions:
        print(f"Processing region: {region}")
        ec2 = boto3.client('ec2', region_name=region)

        volumes = ec2.describe_volumes(
            Filters=[{'Name': 'status', 'Values': ['in-use']}]
        )['Volumes']

        for volume in volumes:
            volume_id = volume['VolumeId']
            print(f"Creating snapshot for Volume: {volume_id}")

            try:
                snapshot = ec2.create_snapshot(
                    VolumeId=volume_id,
                    Description=f"Snapshot of {volume_id} from region {region}"
                )

                snapshots_created.append({
                    "Region": region,
                    "VolumeId": volume_id,
                    "SnapshotId": snapshot['SnapshotId']
                })

                success_msg = (
                    f"Snapshot created: {snapshot['SnapshotId']} "
                    f"for Volume {volume_id} in Region {region}"
                )
                print(success_msg)
                notify_success(success_msg)

            except Exception as e:
                error_msg = (
                    f"Error creating snapshot for Volume {volume_id} "
                    f"in Region {region}: {str(e)}"
                )
                print(error_msg)
                notify_error(error_msg)

    return {
        "statusCode": 200,
        "body": f"Snapshots created: {snapshots_created}"
    }
