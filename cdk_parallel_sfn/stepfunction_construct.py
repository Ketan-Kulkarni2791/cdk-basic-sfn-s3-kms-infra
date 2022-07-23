"""Code for generating the step resources.
This is for creating the various tasks, retry, error
and states that are involved."""

from typing import Dict, Any, List
from aws_cdk import aws_iam as iam
from aws_cdk import aws_stepfunctions as sfn
from aws_cdk.core import Stack, Duration

class StepFunctionConstruct:
    """Class has methods to create a step function."""
    @staticmethod
    def create_step_function(
        stack: Stack,
        env: str,
        config: dict,
        role: iam.Role) -> sfn.StateMachine:
        """Create step Function."""
        
        actuals_func = StepFunctionConstruct.actuals()
        benchmarks_func = StepFunctionConstruct.benchmarks()
        
        # wait_seconds = Duration.seconds(amount=int(5))
        # wait_task_act = sfn.Wait(
        #     scope=stack,
        #     id="Waiting for actuals to finish",
        #     time=sfn.WaitTime.duration(duration=wait_seconds)
        # )
        # wait_task_bench = sfn.Wait(
        #     scope=stack,
        #     id="Waiting for benchmarks to finish",
        #     time=sfn.WaitTime.duration(duration=wait_seconds)
        # )
        
        definition = StepFunctionConstruct.create_step_function_defination(
            stack=stack,
            # actuals_task=actuals_func,
            # benchmarks_task=benchmarks_func,
            # wait_task_act=wait_task_act,
            # wait_task_bench=wait_task_bench
        )
        
        state_machine = sfn.StateMachine(
            scope=stack,
            id=f"{config['global']['app-name']}-stateMachine-Id",
            state_machine_name=f"{config['global']['app-name']}-stateMachine",
            definition=definition,
            role=role
        )
        return state_machine
        
    def actuals():
        return {"statement": "Hello from actuals()."}
                
    
    def benchmarks():
        return {"statement": "Hello from benchmarks()."}
    
    @staticmethod
    def create_step_function_defination(
        stack,
        # actuals_task,
        # benchmarks_task,
        # wait_task_act,
        # wait_task_bench
        ) -> sfn.Chain:
        """Function to create step function defination."""
        exec_param = {"Execution.$": "$$.Execution.Id"}
        
        start_state = sfn.Pass(
            scope=stack,
            id="StartState",
            result_path="$.Execution",
            parameters=exec_param
        )
        success = sfn.Succeed(
            scope=stack,
            id="Step Function Execution Complete."
        )
        
        defination = sfn.Chain.start(
            state=start_state
        ).next(
            next=success
        )
        return defination
    
    @staticmethod
    def get_sfn_lambda_invoke_job_policy_statement(
        config: dict, env: str) -> iam.PolicyStatement:
        """Returns policy statement lambdas used for managing SFN resources and components."""
        policy_statement = iam.PolicyStatement()
        policy_statement.effect = iam.Effect.ALLOW
        policy_statement.add_actions("lambda:InvokeFunction")
        policy_statement.add_resources(config['global']['lambdaFunctionArnBase'])
        return policy_statement
