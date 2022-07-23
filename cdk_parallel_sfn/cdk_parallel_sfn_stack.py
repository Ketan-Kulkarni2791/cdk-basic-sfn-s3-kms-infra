"""Main python file_key for adding resources to the application stack."""
from typing import Dict, Any
from aws_cdk import (
    core,
    aws_kms as kms,
    aws_s3 as s3
)
from constructs import Construct
from .iam_construct import IAMConstruct
from .kms_construct import KMSConstruct
from .stepfunction_construct import StepFunctionConstruct
from .s3_construct import S3Construct


class CdkParallelSfnStack(core.Stack):
    """Build the app stacks and its resources."""
    def __init__(self, env_var: str, scope: core.Construct, 
                 app_id: str, config: dict, **kwargs: Dict[str, Any]) -> None:
        """Creates the cloudformation templates for the projects."""
        super().__init__(scope, app_id, **kwargs)
        self.env_var = env_var
        self.config = config
        CdkParallelSfnStack.create_stack(self, self.env_var, config=config)
        
    @staticmethod
    def create_stack(stack: core.Stack, env: str, config: dict) -> None:
        """Create and add the resources to the application stack"""
        CdkParallelSfnStack.create_iam_user_infra(
            stack=stack, env=env, config=config
        )
        
        kms_key = KMSConstruct.create_kms_key_from_arn(
            stack=stack, env=env, config=config
        )
        
        # Step function Infra setup ----------------------------------------------
        CdkParallelSfnStack.create_step_function(
            stack=stack,
            env=env, 
            config=config,
            kms_key=kms_key
        )
        
        # S3 Bucket Infra Setup --------------------------------------------------
        s3_bucket = CdkParallelSfnStack.create_bucket(
            config=config,
            env=env,
            encryption_key=kms_key,
            dest_bucket_arn=config['global']['bucket_arn'],
            dest_bucket_kms_arn=config['global']['bucketKmsKeyArn'],
            aws_account=config['global']['awsAccount'],
            stack=stack
        )
        
    @staticmethod
    def create_iam_user_infra(
        stack: core.Stack,
        env: str,
        config: dict) -> None:
        """Create IAM user and required attributes"""
        user = IAMConstruct.create_user(stack=stack)
        group = IAMConstruct.create_group(stack=stack)
        group.add_user(user)
        access_policy = IAMConstruct.create_managed_policy(
            stack=stack,
            policy_name="cdk-parallel-sfn-data-access-policy",
            statements=[
                IAMConstruct.get_access_key_mgmt_policy(stack=stack)
            ]
        )
        user.add_managed_policy(access_policy)
        
    @staticmethod
    def create_step_function(
        stack: core.Stack,
        env: str,
        config: dict,
        kms_key: kms.Key) -> None:
        """Create the step function needed for the project."""
        state_machine_policy = IAMConstruct.create_managed_policy(
            stack=stack,
            policy_name="parallel-sfn-stateMachine-policy",
            statements=[
                S3Construct.get_s3_bucket_policy(config['global']['parallelSfnS3Arn']),
                S3Construct.get_s3_object_policy(config['global']['parallelSfnS3Arn']),
                StepFunctionConstruct.get_sfn_lambda_invoke_job_policy_statement(config, env),
                KMSConstruct.get_kms_key_encrypt_decrypt_policy(
                    [
                        kms_key.key_arn,
                        config['global']['parallel-sfn-kms-arn']
                    ]
                )
            ]
        )
        
        state_machine_role = IAMConstruct.create_role(
            stack=stack,
            role_name="parallel-sfn-statemachine-role",
            assumed_by=['states']
        )
        state_machine_role.add_managed_policy(state_machine_policy)
        
        StepFunctionConstruct.create_step_function(
            stack=stack,
            env=env,
            config=config,
            role=state_machine_role
        )
        
    @staticmethod
    def create_bucket(
        config: dict,
        env: str,
        encryption_key: kms.Key,
        dest_bucket_arn: str,
        dest_bucket_kms_arn: str,
        aws_account: str,
        stack: core.Stack) -> s3.Bucket:
        """Create an encrypted s3 bucket."""
        s3_bucket = S3Construct.create_bucket(
            stack=stack,
            bucket_id=f"parallel-sfn-{config['global']['env']}",
            bucket_name=config['global']['bucket_name'],
            bucket_desc=f"for storing files for {config['global']['app-name']}",
            encryption_key=encryption_key,
            dest_bucket_arn=dest_bucket_arn,
            dest_bucket_kms_arn=dest_bucket_kms_arn,
            aws_account=aws_account
        )
        return s3_bucket
