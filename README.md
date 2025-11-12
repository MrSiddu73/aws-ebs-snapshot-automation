> 🧠 **Serverless AWS Backup Automation:** Automatically creates EBS snapshots when EC2 instances start — built using EventBridge + Lambda + SNS.


## 🧠 Overview
This project automatically creates EBS snapshots whenever an EC2 instance starts (state = running).
It checks if the instance has the tag `Backup=true` before creating a snapshot.
After successful snapshot creation, an email is sent using Amazon SNS.

## ⚙️ AWS Services Used
- **EC2** – Virtual machines with attached EBS volumes
- **EBS** – Volume snapshots are created automatically
- **EventBridge** – Detects EC2 instance state changes
- **Lambda** – Runs code that creates snapshots and sends SNS emails
- **SNS** – Sends email notifications about backup status
- **CloudWatch Logs** – Tracks Lambda execution logs

## 🔧 Setup Steps
1. **Create SNS Topic**
   - Go to SNS → Topics → Create topic → Standard → Name it `EBSBackupNotifications`.
   - Create a subscription (Protocol: Email → your email ID).
   - Confirm the subscription from your mailbox.

2. **Create IAM Role for Lambda**
   - Go to IAM → Roles → Create role → Lambda.
   - Attach the policy from `iam_policy.json`.

3. **Create Lambda Function**
   - Runtime: Python 3.9
   - Upload code from `lambda_function.py`.
   - Set environment variable:  
     `SNS_TOPIC_ARN = arn:aws:sns:REGION:ACCOUNT_ID:EBSBackupNotifications`
   - Assign the IAM role you created.

4. **Create EventBridge Rule**
   - Go to EventBridge → Rules → Create rule.
   - Paste JSON from `eventbridge_rule.json`.
   - Add your Lambda function as the target.

5. **Tag your EC2 Instance**
   - Add tag:  
     `Key = Backup`  
     `Value = true`

6. **Test**
   - Stop → Start your EC2 instance.
   - Check CloudWatch Logs for output.
   - Go to EC2 → Snapshots → confirm snapshot created.
   - Check your email → you’ll get a success notification.

## **ARCHITECTURE DIAGRAM**
EC2 (Backup=true) → EventBridge Rule → Lambda (create snapshot) → SNS Topic (Email Notification)
                                         ↓
                                      EBS Snapshot


## 📊 Log Output
   - Event: {...}
     Instance tags: {'Backup': 'true'}
     Created snapshot: snap-0123abcd4567efgh


## 📬 Example Email
**Subject:** EBS Snapshot Created  
**Message:** Created snapshots ['snap-0123abcd4567efgh'] for instance i-0abcd1234567efgh.

## ✅ Features
- Event-driven (no cron jobs)
- ### 🔖 Tag-Filter Logic  
The Lambda checks both `Backup=true` and `backup=true` tags, ensuring no instance is skipped due to tag-key case mismatch.
- Email notification via SNS
- Serverless (no EC2 maintenance)
- Logs every action in CloudWatch

## 🚀 Future Improvements
- Add cleanup Lambda to delete old snapshots
- Add SNS notification for failures
- Add Terraform/CloudFormation automation

🧭 SIMPLE SETUP CHECKLIST (step-by-step summary)
| Step | Action                                                    | Where               |
| ---- | --------------------------------------------------------- | ------------------- |
| 1️⃣  | Create **SNS Topic** and confirm email                    | SNS console         |
| 2️⃣  | Create **IAM Role** with `iam_policy.json`                | IAM console         |
| 3️⃣  | Create **Lambda Function** with `lambda_function.py`      | Lambda console      |
| 4️⃣  | Add environment variable `SNS_TOPIC_ARN`                  | Lambda config       |
| 5️⃣  | Attach IAM Role to Lambda                                 | Lambda permissions  |
| 6️⃣  | Create **EventBridge Rule** using `eventbridge_rule.json` | EventBridge console |
| 7️⃣  | Add tag `Backup=true` to EC2 instance                     | EC2 console         |
| 8️⃣  | Start EC2 → verify snapshot + email                       | EC2 & email inbox   |


## 🧩 Contributions and Implementation
This project was developed and customized by **Siddu S.N**, who:
- Modified Lambda logic to handle tag keys (`Backup` or `backup`).
- Integrated Amazon SNS for real-time email notifications.
- Implemented least-privilege IAM policy for Lambda.
- Structured repository with clear folders (`lambda`, `iam`, `eventbridge`).
- Documented setup and testing process for reproducibility.

