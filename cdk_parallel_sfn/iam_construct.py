"""Module to hold helper methods for CDK IAM creation"""
from typing import Dict, Any, List
from aws_cdk import aws_iam as iam
from aws_cdk.core import Stack

class IAMConstruct:
    """Clas holds methods for IAM resource creation"""
    
    @staticmethod
    def create_group(
        stack: Stack) -> None:
        """Group for CDK Basic Setup IAM user"""
        user_group = iam.Group(
            scope=stack,
            id="cdk-parallel-sfn-group-id",
            group_name="cdk-parallel-sfn-iam-group"
        )
        return user_group
    
    @staticmethod
    def create_user(
        stack: Stack) -> None:
        """Create user utilized for CDK Basic Setup data access"""
        user = iam.User(
            scope=stack,
            id="cdk-parallel-sfn-user-id",
            user_name="cdk-parallel-sfn-iam-user"
        )
        return user
    
    @staticmethod
    def create_role(
        stack: Stack,
        role_name: str,
        assumed_by: List[str]) -> iam.Role:
        """Create role utilized by IAM users and group."""
        services = list(map(lambda x: iam.ServicePrincipal(
            f"{x}.amazonaws.com"), assumed_by))
        role = iam.Role(
            scope=stack,
            id=f"{role_name}-id",
            assumed_by=iam.CompositePrincipal(*services)
        )
        return role
    
    @staticmethod
    def create_managed_policy(stack: Stack, policy_name: str,
                              statements: List[iam.PolicyStatement]) -> iam.PolicyStatement:
        """Create managed policy for IAM users"""
        policy = iam.ManagedPolicy(
            scope=stack,
            id=f"{policy_name}-id",
            statements=statements
        )
        return policy
    
    @staticmethod
    def get_access_key_mgmt_policy(stack: Stack) -> iam.PolicyStatement:
        """To generate secrets using secrets admin role, below permissions needed."""
        policy_statement = iam.PolicyStatement()
        policy_statement.effect = iam.Effect.ALLOW
        policy_statement.add_actions("iam:DeleteAccessKey")
        policy_statement.add_actions("iam:GetAccessKeyLastUsed")
        policy_statement.add_actions("iam:UpdateAccessKey")
        policy_statement.add_actions("iam:CreateAccessKey")
        policy_statement.add_actions("iam:ListAccessKey")
        policy_statement.add_resources(
            f"arn:aws:iam::{stack.account}:user/${{aws:username}}"
        )
        policy_statement.add_resources(
            f"arn:aws:iam::{stack.account}:user/parallel-sfn/${{aws:username}}"
        )
        return policy_statement