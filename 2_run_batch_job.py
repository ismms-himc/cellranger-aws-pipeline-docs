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

# pass information to job
run_arguments = {'inst_arg_key':'inst_arg_val'}

# the params_dict dictionary is passed to the job
##################################################
params_dict = {}
params_dict['inst_key'] = json.dumps(run_arguments)

# job 1
#########################
# this used to be the 10GB job (which had an out of memory error)
base_name = 'cellranger-UPLOAD-RESULTS'
batch_job_name = base_name + '-10GB'
job_response = client_batch.submit_job(jobDefinition=job_def_id,
                                       jobName=batch_job_name,
                                       jobQueue=job_queue_id,
                                       parameters=params_dict)

job_id_1 = job_response['jobId']
print('submitted job 1: ' + batch_job_name)
