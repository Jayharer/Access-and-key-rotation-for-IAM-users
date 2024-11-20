import boto3
from datetime import date

from src import config


def getMailBody(subject: str, body: str) -> dict:
    return {
        'Simple': {
            'Subject': {
                'Data': subject,
                'Charset': 'UTF-8'
            },
            'Body': {
                'Html': {
                    'Data': body,
                    'Charset': 'UTF-8'
                }
            }
        }
    }


def getEmailContent(is_warning: bool, key_data: dict) -> dict:
    if is_warning:
        subject = 'Your AWS account access key & secret key going to expire soon..'
        body = 'Generate new access key as soon as possible'
    else:
        subject = 'Your AWS account new access key & secret key'
        body = '<p> Old access key expired & New access key generated </p><br>' + \
               '<p> AccessKey : ' + key_data["access_key"] + '</p><br>' + \
               '<p> SecretKey : ' + key_data["secret_key"] + '</p><br>' + \
               '<p> Update all applications with new Keys </p>'
    mail_body = getMailBody(subject, body)
    return mail_body


def sendMail(sender: str, receiver: str, key_data: dict, is_warning: bool):
    client = boto3.client('pinpoint-email', region_name=config.aws_region)
    content = getEmailContent(is_warning, key_data)
    try:
        client.send_email(
            FromEmailAddress=sender,
            Destination={'ToAddresses': [receiver]},
            ReplyToAddresses=[sender],
            FeedbackForwardingEmailAddress=sender,
            Content=content,
            ConfigurationSetName=''
        )
    except Exception as e:
        print(repr(e))
    else:
        print("Email sent!")

