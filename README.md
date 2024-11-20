# Access-and-key-rotation-for-IAM-users
Access/Secret key rotation &amp; console access strategy for IAM usrs.


We require two lambda script as per below details.

1. User inactive for 30 days -> disable console login, disable mfa
2. Secret & Access keys not rotated for 60 days -> Send Email with First Warning on 50th Day to IAM user and then rotate.

Note: IAM user will receive  from IAM user tag value which has Key=Owner & Value=EmailID.

Note : we can use AWS SES or AWS pinpoint to send Email to IAM User as per tag basis.

Updated Task2 key Rotation code as per new requirements
 1. Key rotation exclude for console disable user
 2. Use of pinpoint instead of SES for sending mail

note : destination mail id must verified in pinpoint


AWS resources used:
    - eventbridge
    - IAM Roles/Policies
    - AWS pinpoint
    - AWS lambda

Tools used:
    IAC: terraform
    scm: Git

