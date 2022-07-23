import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_parallel_sfn.cdk_parallel_sfn_stack import CdkParallelSfnStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_parallel_sfn/cdk_parallel_sfn_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CdkParallelSfnStack(app, "cdk-parallel-sfn")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
