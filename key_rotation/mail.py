import boto3
import os
import traceback

from common import config
from . import ses_verify as ses


def getMailBody(subject: str, body_html: str) -> dict:
    return {
        'Subject': {
                'Charset': 'UTF-8',
                'Data': subject
            },
        'HtmlPart': {
            'Charset': 'UTF-8',
            'Data': body_html
        },
        'TextPart': {
            'Charset': 'UTF-8',
            'Data': ""
        }
    }


def getEmailContent(is_warning: bool, key_data: dict) -> dict:
    if is_warning:
        subject = 'Your AWS account access key & secret key going to expire soon..'
        body = 'Generate new access key as soon as possible'
    else:
        subject = 'Your AWS account new access key & secret key'
        body = f""" Old access key expired & New access key generated
                   AccessKey : {key_data["access_key"]} 
                   SecretKey : {key_data["secret_key"]}
                   Update all applications with new Keys """
    mail_body = getMailBody(subject, body)
    return mail_body


def sendMail(receiver: str, key_data: dict, is_warning: bool):
    client = boto3.client('pinpoint', region_name=config.aws_region)
    content = getEmailContent(is_warning, key_data)
    app_id = os.getenv('PINPOINT_APP_ID', '62f4233bcae346d6b98bfd205d3b2e06')
    try:
        resp = client.send_messages(
            ApplicationId=app_id,
            MessageRequest={
                'Addresses': {
                    receiver: {
                        'ChannelType': 'EMAIL'
                    }
                },
                'MessageConfiguration': {
                    'EmailMessage': {
                        'FromAddress': config.sender_mail,
                        'SimpleEmail': content,
                    }
                }
            }
        )
        print(f"Email sent for {receiver}!", resp)
    except Exception as e:
        print(traceback.format_exc())


def mailerService(user_email: str, key_data: dict, is_warning: bool):
    if user_email == "":
        return
    ses_identity = ses.SesIdentity(ses_client=boto3.client("ses"))
    status = ses_identity.getIdentityStatus(user_email)
    print(f"{user_email} has status: {status}.")

    if status == "Success":
        sendMail(user_email, key_data, is_warning)
    else:
        ses_identity.verifyEmailIdentity(user_email)
