import boto3
import glob
import json

client_cf = boto3.client('cloudformation')
client_batch = boto3.client('batch')

stack_name = 'cellranger-job'

# Get stack info from cloudformation
##############################################
stack_info = client_cf.describe_stack_resources(StackName=stack_name)
resources = stack_info['StackResources']

for inst_resource in resources:
  resource_type = inst_resource['ResourceType']
  logical_resource_id = inst_resource['LogicalResourceId']

  # job 1
  if logical_resource_id == 'JobDef1':
    job_def_id = inst_resource['PhysicalResourceId'].split('/')[-1].split(':')[0]

  if resource_type == 'AWS::Batch::JobQueue':
    job_queue_id = inst_resource['PhysicalResourceId'].split('/')[-1].split(':')[0]


# single-sample-job initialization
####################################
base_name = 'cellranger-UPLOAD-RESULTS'
params_dict = {}
params_dict['bucket'] = 'cellranger-tiny-bucket'

# job 1
#########################
# this used to be the 10GB job (which had an out of memory error)
batch_job_name = base_name + '-10GB'
job_response = client_batch.submit_job(jobDefinition=job_def_id,
                                       jobName=batch_job_name,
                                       jobQueue=job_queue_id,
                                       parameters={'inst_key':'inst_value'})


job_id_1 = job_response['jobId']
print('submitted job 1: ' + batch_job_name)
