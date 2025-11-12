import boto3
import datetime
import os

# AWS clients
ec2 = boto3.client('ec2')
sns = boto3.client('sns')

# Environment variable (set inside Lambda console)
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')

def lambda_handler(event, context):
    try:
        print("Event:", event)
        detail = event.get('detail', {})
        instance_id = detail.get('instance-id')

        if not instance_id:
            print("No instance ID found in event.")
            return {"status": "no-instance-id"}

        # Get instance details
        response = ec2.describe_instances(InstanceIds=[instance_id])
        instance = response['Reservations'][0]['Instances'][0]
        tags = {t['Key']: t['Value'] for t in instance.get('Tags', [])}
        print("Instance tags:", tags)

        # Check if tag Backup=true (case-insensitive)
        if tags.get('Backup', tags.get('backup')) != 'true':
            print(f"Skipping snapshot for {instance_id}; Backup tag not present/true.")
            return {"status": "skipped-no-tag"}

        # Get all attached EBS volumes
        volumes = [v['Ebs']['VolumeId'] for v in instance['BlockDeviceMappings']]
        created_snaps = []

        # Create snapshot for each volume
        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")
        for vol in volumes:
            description = f"AutoBackup-{instance_id}-{vol}-{timestamp}"
            snap = ec2.create_snapshot(VolumeId=vol, Description=description)
            snap_id = snap['SnapshotId']
            ec2.create_tags(Resources=[snap_id], Tags=[
                {'Key': 'Name', 'Value': description},
                {'Key': 'CreatedBy', 'Value': 'LambdaAutomation'},
                {'Key': 'InstanceId', 'Value': instance_id}
            ])
            print(f"Created snapshot: {snap_id}")
            created_snaps.append(snap_id)

        # Send SNS notification (optional)
        if SNS_TOPIC_ARN:
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject="EBS Snapshot Created",
                Message=f"Created snapshots {created_snaps} for instance {instance_id}"
            )

        return {"status": "success", "snapshots": created_snaps}

    except Exception as e:
        print("Error:", str(e))
        if SNS_TOPIC_ARN:
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject="EBS Snapshot Failure",
                Message=f"Error creating snapshot: {str(e)}"
            )
        raise
