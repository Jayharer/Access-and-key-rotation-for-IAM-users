# Access-and-key-rotation-for-IAM-users

## Requirements
Assume 10 to 100 IAM users in your account and 
you have to manges there access as per compliance

1. IAM User inactive for 30 days -> disable console login, disable mfa
2. Secret & Access keys not rotated for 60 days -> First Warning on 50th Day
   -> Above 60 day send mail with new access key & delete old acces key.
3. Key rotation exclude for console disable user.
---

## Design
- Two lambda functions
    1. To manage IAM user console Access.
    2. To mange Access key compliance & rotation.
- Evenet bridge that trigget both lambda function at 6pm every day.
- Dynamodb that store newly created access keys.
- IAM user do't have inbuit email, that's why each user we add tag **Email**
  with corresponding mail id as value
- Pinpont & SES to verify & sending mail to IAM user.
- SAM cli to create & deploy lambda functions.
- terraform to create & deploy event bridge resources.
---

## Tools
1. AWS Cloud
2. SAM & SAM Cli
3. Terraform
4. Git
5. Python
6. AWS SDK (boto3)
---

## AWS services used
1. IAM
2. Lambda Functions
3. SES
4. Pinpoint
5. Dynamodb
6. EventBridge
7. S3 Bucket
7. CloudeWatch
---

### Architecture
![alt text](img/IAMAccessAndKeyRotation.svg)

---

## Installation

### 1. Clone repo
```bash
git clone https://github.com/Jayharer/Access-and-key-rotation-for-IAM-users.git
```

### 2. Install aws cli & configure default profile

### 3. Install sam cli

### 4. Manually create s3 bucket in aws
Update **src/samconfig.toml** with
```
s3_bucket = "your-s3-bucket-name"
```

Update **iac/backend.tf** with
```
bucket = "your-s3-bucket-name"
```

## 4. Deploy lambda functions
```bash
cd src
sam build
sam deploy
```

## 4. Terraform IAC
```bash
cd iac 
terraform init
terraform plan 
terraform apply
```
---

## Clean up
Delete all resources from AWS cloud
```bash
aws cloudformation delete-stack --stack-name sam-app
cd iac 
terraform destroy
```