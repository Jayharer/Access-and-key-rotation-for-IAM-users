import boto3, os, sys
from datetime import date

aws_root_account_id = 861936062471

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def disableConsoleLogin(client: boto3.client, user_name: str):
    try:
        resp1 = client.delete_login_profile(
            UserName=user_name)
    except Exception as e:
        pass


def disableMFA(client: boto3.client, user_name: str):
    try:
        resp2 = client.deactivate_mfa_device(
            UserName=user_name,
            SerialNumber='arn:aws:iam::{}:mfa/{}'.format(
                aws_root_account_id, user_name)
        )
    except Exception as e:
        pass


def lambda_handler(event, context):
    iam_client = boto3.client('iam')
    list_users = iam_client.list_users()
    for user in list_users['Users']:
        print("user", user)
        user_name = user['UserName']
        if 'PasswordLastUsed' in user.keys():
            password_last_used = (user['PasswordLastUsed']).date()
            today = date.today()
            day_difference = (today - password_last_used).days
            if day_difference >= 60:
                disableConsoleLogin(iam_client, user_name)
                disableMFA(iam_client, user_name)
                print("login & mfa disable for user : {}".format(user_name))
    return {'statusCode': 200, 'msg': 'success console access'}


if __name__ == "__main__":
    lambda_handler({}, None)
