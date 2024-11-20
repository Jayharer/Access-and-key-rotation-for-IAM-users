import boto3
from botocore.exceptions import ClientError
from datetime import date

from . import mail
from src import config


def getKeyData(client: boto3.client, user_name: str) -> list:
    resp_access_keys = client.list_access_keys(UserName=user_name)
    access_key_list = list()
    for data in resp_access_keys['AccessKeyMetadata']:
        key_id = data['AccessKeyId']
        key_create_date = data['CreateDate'].date()
        key_status = data['Status']
        key_duration = (date.today() - key_create_date).days
        access_key_list.append({'key_id': key_id, 'key_create_date': key_create_date,
                                'key_status': key_status, 'key_duration': key_duration
                                })
    return access_key_list


def checkConsoleAccess(client: boto3.client, user_name: str) -> bool:
    # get login profile of user to identity console disable user
    try:
        resp = client.get_login_profile(UserName=user_name)
        return True
    except ClientError as e:
        print('{} do not have login console access'.format(user_name))
        return False


def getUserEmail(client: boto3.client, user_name: str) -> str:
    user_email = ""
    response_tag = client.get_user(UserName=user_name)
    print("response_tag", response_tag)
    if 'Tags' in response_tag['User'].keys():
        for tag in response_tag['User']['Tags']:
            if tag['Key'].lower() == 'owner':
                user_email = tag['Value']
    return user_email


def generateNewKey(client: boto3.client, user_name: str, table):
    new_key = client.create_access_key(UserName=user_name)
    # store key into dynamo_db table
    table.put_item(
        Item={
            'user_name': user_name,
            'key_id': new_key['AccessKey']['AccessKeyId'],
            'secret_key': new_key['AccessKey']['SecretAccessKey'],
            'create_date': new_key['AccessKey']['CreateDate'].date().strftime('%Y-%m-%d')
        })
    return new_key


def disableAccessKey(client: boto3.client, user_name: str,
                     access_key_id: str):
    client.update_access_key(
        AccessKeyId=access_key_id,
        Status='Inactive',
        UserName=user_name, )


def deleteInactiveAccessKey(username: str, access_key_id: str, table):
    iam_client = boto3.client('iam')
    iam_client.delete_access_key(UserName=username,
                                 AccessKeyId=access_key_id)
    # delete key from dynamodb table users
    try:
        table.delete_item(
            Key={
                'username': username,
                'keyid': access_key_id
            }
        )
    except Exception as e:
        print(repr(e))


def warningAndRotation(client: boto3.client, user_data: dict,
                       access_key: dict, table):
    sender_mail = user_data["sender_mail"]
    user_mail = user_data["user_mail"]
    user_name = user_data["user_name"]
    is_key_expiring_soon = access_key['key_duration'] >= 50
    is_key_expired = access_key['key_duration'] >= 60
    if is_key_expired:
        if user_data["is_console_access"]:
            new_key = generateNewKey(client, user_name, table)
            key_data = {
                "access_key": new_key['AccessKey']['AccessKeyId'],
                "secret_key": new_key['AccessKey']['SecretAccessKey']
            }
            mail.sendMail(sender_mail, user_mail, key_data,
                          is_warning=False)
            deleteInactiveAccessKey(user_name,
                                           access_key["keyid"], table)
        else:
            # disable access keys for console disable user
            disableAccessKey(client, user_name, access_key["keyid"])
    elif is_key_expiring_soon:
        mail.sendMail(sender_mail,
                      user_mail, key_data=dict(), is_warning=True)


def lambda_handler(event, context):
    iam_client = boto3.client('iam')
    list_users = iam_client.list_users()
    sender_mail = config.sender_mail

    dynamo_db = boto3.resource('dynamodb')
    table = dynamo_db.Table('users_keys')

    for user in list_users['Users']:
        user_name = user['UserName']
        user_data = dict()
        user_data["access_key_list"] = getKeyData(user_name, iam_client)
        user_data["user_mail"] = getUserEmail(iam_client, user_name)
        user_data["is_console_access"] = checkConsoleAccess(iam_client, user_name)
        user_data["user_name"] = user_name
        for access_key in user_data["access_key_list"]:
            warningAndRotation(iam_client, user_data, access_key, table)

    return {
        'statusCode': 200,
        'msg': 'success key rotation',
    }
