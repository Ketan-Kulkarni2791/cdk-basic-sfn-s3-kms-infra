"""Module for creating KMS encryption key"""
from typing import List
from aws_cdk import aws_iam as iam
from aws_cdk import aws_kms as kms 
from aws_cdk.core import Stack

class KMSConstruct:
    """Class for methods to create KMS keys"""
    @staticmethod
    def create_kms_key_from_arn(
        stack: Stack,
        env: str,
        config: dict) -> kms.Key:
        """Import KMS key from external stack, used for encrypting AWS resources."""
        return kms.Key.from_key_arn(
            scope=stack,
            id=f"{config['global']['app-name']}-keyId",
            key_arn=config["global"]["parallel-sfn-kms-arn"]
        )
        
    @staticmethod
    def get_kms_key_encrypt_decrypt_policy(
        kms_keys: List[str]) -> iam.PolicyStatement:
        """Returns policy statement for encrypting and decrypting kms keys."""
        policy_statement = iam.PolicyStatement()
        policy_statement.effect = iam.Effect.ALLOW
        policy_statement.add_actions("kms:Decrept")
        policy_statement.add_actions("kms:Encrypt")
        policy_statement.add_actions("kms:ReEncrypt*")
        policy_statement.add_actions("kms:GenerateDataKey*")
        for key in kms_keys:
            policy_statement.add_resources(key)
        return policy_statement