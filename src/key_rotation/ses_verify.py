import boto3
import logging
from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)


class SesIdentity:

    def __init__(self, ses_client):
        self.ses_client = ses_client

    def verifyEmailIdentity(self, email_address):
        try:
            self.ses_client.verify_email_identity(EmailAddress=email_address)
            logger.info("Started verification of %s.", email_address)
        except ClientError:
            logger.exception("Couldn't start verification of %s.", email_address)

    def getIdentityStatus(self, identity):
        try:
            response = self.ses_client.get_identity_verification_attributes(
                Identities=[identity]
            )
            status = response["VerificationAttributes"].get(
                identity, {"VerificationStatus": "NotFound"}
            )["VerificationStatus"]
            logger.info("Got status of %s for %s.", status, identity)
        except ClientError:
            logger.exception("Couldn't get status for %s.", identity)
            raise
        else:
            return status

