import os
import sys
from datetime import date

import boto3

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from . import mail


class KeyRotation:
    def __init__(self, iam_client: boto3.client):
        self.client = iam_client

    def getKeyData(self, user_name: str) -> list:
        resp_access_keys = self.client.list_access_keys(UserName=user_name)
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

    def getUserEmail(self, user_name: str) -> str:
        response_tag = self.client.get_user(UserName=user_name)
        if 'Tags' in response_tag['User'].keys():
            for tag in response_tag['User']['Tags']:
                if tag['Key'].lower() == 'email':
                    return tag['Value']
        return ""

    def checkConsoleAccess(self, user_name: str) -> bool:
        # get login profile of user to identity console disable user
        try:
            resp = self.client.get_login_profile(UserName=user_name)
            return True
        except Exception as e:
            return False

    def generateNewKey(self, user_name: str, table):
        new_key = self.client.create_access_key(UserName=user_name)
        # store key into dynamo_db table
        table.put_item(
            Item={
                'user_name': user_name,
                'key_id': new_key['AccessKey']['AccessKeyId'],
                'secret_key': new_key['AccessKey']['SecretAccessKey'],
                'create_date': new_key['AccessKey']['CreateDate'].date().strftime('%Y-%m-%d')
            })
        return new_key

    def disableAccessKey(self, user_name: str,
                         access_key_id: str):
        try:
            self.client.update_access_key(
                AccessKeyId=access_key_id,
                Status='Inactive',
                UserName=user_name, )
        except Exception as e:
            print(repr(e))

    def deleteInactiveAccessKey(self, username: str, access_key_id: str, table):
        self.client.delete_access_key(UserName=username,
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

    def warningAndRotation(self, user_data: dict,
                           access_key: dict, table):
        user_mail = user_data["user_mail"]
        user_name = user_data["user_name"]
        is_key_expiring_soon = access_key['key_duration'] >= 30
        is_key_expired = access_key['key_duration'] >= 60
        if is_key_expired:
            if user_data["is_console_access"]:
                new_key = self.generateNewKey(user_name, table)
                key_data = {
                    "access_key": new_key['AccessKey']['AccessKeyId'],
                    "secret_key": new_key['AccessKey']['SecretAccessKey']
                }
                mail.mailerService(user_mail, key_data, is_warning=False)
                self.deleteInactiveAccessKey(user_name,
                                             access_key["keyid"], table)
            else:
                print('{} do not have login console access disabling access key : {}'.format(
                    user_name, access_key["keyid"]))
                # disable access keys for console disable user
                self.disableAccessKey(user_name, access_key["keyid"])
        elif is_key_expiring_soon:
            print(f'Key expiring soon for user:{user_mail}')
            mail.mailerService(user_mail, key_data=dict(), is_warning=True)


def lambda_handler(event, context):
    iam_client = boto3.client('iam')
    key_rotation = KeyRotation(iam_client=iam_client)
    list_users = iam_client.list_users()
    dynamo_db = boto3.resource('dynamodb')
    table = dynamo_db.Table('accessKeys')
    for user in list_users['Users']:
        user_name = user['UserName']
        user_data = dict()
        user_data["access_key_list"] = key_rotation.getKeyData(user_name)
        user_data["user_mail"] = key_rotation.getUserEmail(user_name)
        user_data["is_console_access"] = key_rotation.checkConsoleAccess(user_name)
        user_data["user_name"] = user_name
        for access_key in user_data["access_key_list"]:
            key_rotation.warningAndRotation(user_data, access_key, table)

    return {
        'statusCode': 200,
        'msg': 'success key rotation',
    }
