# Cellranger AWS Pipeline

This repo sets up and runs cellranger (mkfastq and count) on the tiny-bcl example using AWS batch. In a separate repo, [dockerized-cellranger](https://github.com/ismms-himc/dockerized_cellranger), we ran `cellranger mkfastq` and `cellranger count` in a docker container using the `tiny-bcl` example dataset. This repo is also builds upon the tutorial branch of [cellranger-aws-pipeline](https://github.com/ismms-himc/cellranger-aws-pipeline/tree/tutorial).

# 1. Upload Data to S3 Bucket (optional)
Nick uploaded the necessary data for running cellranger on tiny-bcl:
* reference transcriptome
* sample-sheet/simple-csv
* tiny-bcl
* cellranger 2.1.0 software (will be copied into docker container)

### Create a new S3 bucket.
Nick has already made the bucket `cellranger-tiny-bucket` and uploaded the data (including the ouputs from mkfasq and count).

### How to upload data to S3 (optional)
`aws s3 cp --recursive cellranger_bucket/ s3://cellranger-tiny-bucket --profile himc`

### How to download from S3 (optional)
`aws s3 cp --recursive s3://cellranger-tiny-bucket cellranger-tiny-bucket --profile himc`

The `--profile himc` is only used if you have several profiles set up on your AWS CLI. 

# 2. Make AMI with 1TB Volume (optional)

We need to make a custom AMI with a 1TB drive attached in order to run cellranger. We will use an existing custom AMI (ami id `ami-0d36b4f4d3b46109a` - this is used in production) instead of making a new custom AMI. For instructions on making the custom AMI see below. 

The custom AMI image id needs to be put into the cloudformation JSON (*cf_cellranger.json*) under the `ComputeEnvironment` key: 
```
    "ComputeEnvironment": {
      "Type": "AWS::Batch::ComputeEnvironment",
      "Properties": {
        "Type": "MANAGED",

        "ComputeResources": {
          "Type": "EC2",
          "MinvCpus": 0,
          "DesiredvCpus": 0,
          "MaxvCpus": 128,
          "InstanceTypes": [
            "optimal"
          ],
          "Subnets": [
            {
              "Ref": "Subnet"
            }
          ],
          "SecurityGroupIds": [
            {
              "Ref": "SecurityGroup"
            }
          ],
          "InstanceRole": {
            "Ref": "IamInstanceProfile"
          },
          "ImageId": "ami-0d36b4f4d3b46109a"
        },

        "ServiceRole": {
          "Ref": "BatchServiceRole"
        }
      }
    }
  ```

# 3. Build Stack using Cloudformation
The following AWS CLI commands can be used to create and update the cloudformation stack on AWS.

### Create the stack
Creat the stack using the `cf_cellranger.json` cloudformation:

`$ aws cloudformation create-stack --template-body file://cf_cellranger.json --stack-name cellranger-job --capabilities CAPABILITY_NAMED_IAM`

### Update the existing stack

`$ aws cloudformation update-stack --template-body file://cf_cellranger.json --stack-name cellranger-job --capabilities CAPABILITY_NAMED_IAM`

# 4. Make and Run Docker Image that will be used as the Batch Job Definition
Use the following docker commands to build and run the container. Here, `<URI>` refers to your _Account ID_.

*** Make sure you have the file `cellranger-2.1.0.tar.gz` in the directory (the file is ~700MB so it is not included in the repo).

`$ docker build -t <URI>.dkr.ecr.us-east-1.amazonaws.com/awsbatch/cellranger-aws-pipeline .`

`$ docker run -it --rm -p 8087:80 <URI>.dkr.ecr.us-east-1.amazonaws.com/awsbatch/cellranger-aws-pipeline`

See the next section for the commands to run within the container.

# 5. Create repository
 Run `python 1_make_ecr_dockerized_cellranger.py`.

 ** This fails for me since I already create it.

# 6. Push Image to AWS ECS

After the image has been built it needs to be pushed to AWS ECS. First auth credentials need to be obtained by running

`$ aws ecr get-login`

This will return a long aws CLI command that you need to copy and paste into the terminal. You may need to remove `-e none` from the command if docker gives an error. Now that you have the proper credentials, you will be able to push the repository using the following command:

`$ docker push <URI>.dkr.ecr.us-east-1.amazonaws.com/awsbatch/cellranger-aws-pipeline`

# 6. Run Cellranger Commands in Container (optional)

These Cellranger commands can be run after changing directories to the `scratch` directory. They will be run by `run_cellranger_pipeline.py`, which currently only copies the reference genome from S3.

### Cellranger mkfastq
`$ cellranger mkfastq --id=tiny-bcl-output --run=tiny-bcl/cellranger-tiny-bcl-1.2.0/ --csv=tiny-bcl/cellranger-tiny-bcl-samplesheet-1.2.0.csv`

### Cellranger count
`$ cellranger count --id=test_sample --fastqs=tiny-bcl-output/outs/fastq_path/p1/s1 --sample=test_sample --expect-cells=1000 --localmem=3 --chemistry=SC3Pv2 --transcriptome=refdata-cellranger-GRCh38-1.2.0`

Note: The samplesheet 10X provides for the tiny-bcl example is more complex than
the samplesheets we provide during our own runs of the cellranger pipeline. As of
02/22/18, we create these sample sheet csv files manually on the command line using
data from Laura's "10x Chromium scRNA-Seq" google sheet ("Sequencing Prep & QC"
tab) under the ismmshimc@gmail.com gmail account. We plan to automate this task
along with various others (i.e. filling out the `cellranger count` parameter
`expect-cells` ) once the AWS pipeline is streamlined. The sample sheet
should look like the below example:

```
[Data]
Lane,Sample_ID,Sample_Name,index
,SI-GA-B6,MC68NN1,SI-GA-B6
,SI-GA-B7,MC68NN2,SI-GA-B7
,SI-GA-B8,MC68TN1,SI-GA-B8

```
To date (02/22/18), the following has been true of the sample sheets:
- The `Lane` column is empty
- `Sample_ID` and `Index` columns have the same value and are always prefixed
with `SI-GA-`

# 7. Submit Batch Job using boto

# Additional Information

## System Requirements (from [10X Genomics](https://support.10xgenomics.com/single-cell-gene-expression/software/overview/system-requirements))

## System Requirements

Cell Ranger
Cell Ranger pipelines run on Linux systems that meet these minimum requirements:

8-core Intel or AMD processor (16 recommended)
64GB RAM (128GB recommended)
1TB free disk space
64-bit CentOS/RedHat 5.5 or Ubuntu 10.04
The pipelines also run on clusters that meet these minimum requirements:

8-core Intel or AMD processor per node
6GB RAM per core
Shared filesystem (e.g. NFS)
SGE or LSF
In addition, Cell Ranger must be run on a system with the following software pre-installed:

Illumina bcl2fastq
bcl2fastq 2.17 or higher is preferred and supports most sequencers running RTA version 1.18.54 or higher. If you are using a NovaSeq, please use version 2.20 or higher. If your sequencer is running an older version of RTA, then bcl2fastq 1.8.4 is required by Illumina.

All other software dependencies come bundled in the Cell Ranger package.

## Components

Modified from from dockerfile: https://hub.docker.com/r/litd/docker-cellranger/

10X Genomics Cell Ranger Suite

bcl2fastq2 v2.19 (06/13/2017)

cellranger v2.1.0

## Making Custom AMI
The cloudformation template sets up the mounted volume for the jobs (see jobdefinition in template) and tells batch to use a custom AMI that has a mounted 1TB volume for the compute environment. See [aws-batch-genomics](https://aws.amazon.com/blogs/compute/building-high-throughput-genomic-batch-workflows-on-aws-batch-layer-part-3-of-4/) part 3 to see how to make a custom AMI. Also see the [cloudformation docs](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-batch-computeenvironment.html) for an exmaple of how to use a custom AMI as a compute environment for AWS batch.

While in the AWS console, go to the EC2 service section. Click "Instances" on the
left-hand side panel. Then hit the blue "Launch Instance" button near the top of the page.
Then, on the left menu, click on "AWS Marketplace".

- Step 1 (choose AMI): select "Amazon ECS-Optimized Amazon Linux AMI".
- Step 2 (choose an instance type): select t2.micro
- Step 3 (skip)
- Step 4 (add storage): Two entries must be made as per [this AWS tutorial](https://aws.amazon.com/blogs/compute/building-high-throughput-genomic-batch-workflows-on-aws-batch-layer-part-3-of-4/)
Follow the screenshot they provide.

**IMPORTANT:** Although 2 storage units are defined in the tutorial (one with 22GB and other with 1000GB):

![AWS AMI Storage Setup](batch_ecs_setup.png)

After running the proposed list of commands:

```
sudo yum -y update
sudo mkfs -t ext4 /dev/xvdb
sudo mkdir /docker_scratch
sudo echo -e '/dev/xvdb\t/docker_scratch\text4\tdefaults\t0\t0' | sudo tee -a /etc/fstab
sudo mount –a
sudo stop ecs
sudo rm -rf /var/lib/ecs/data/ecs_agent_data.json
```

If you run `df -h`, only the first mounted storage unit (in their case, the 22BG image) will be listed.

- Final Step (only steps 1, 2, and 4 needed prior to this): Click "Review and
Launch" and then "Launch". You will be prompted to select an existing key pair
or create a new pair.
  - If creating a new key pair, ensure to save the pem file
  for future use and run `chmod 400` on the pem file. You can then
  hit "Launch Instance" and ssh into your instance.

Again, in the EC2 service section, click "Instances" on the left-hand side panel.
You should now see the instance you created in the last step. Select the instance,
click "Actions" (near the blue "Launch Instance" button), hover over "Image", click
"Create Image". Fill in the "Image name" field and click the "Create Image" button.

Ensure to replace the AMI ID fields in the `cf_cellranger.json` file with the ID of the
AMI you just created. To find the AMI ID, in the EC2 service section, under "Images"
on the left-hand side panel, click "AMIs", and copy the AMI ID corresponding to
the AMI you just created.

Reminder: Don't forget to update the stack via the following command:
`$ aws cloudformation update-stack --template-body file://cf_cellranger.json --stack-name cellranger-job --capabilities CAPABILITY_NAMED_IAM`


Other helpful links:

* [aws London pop-up video batch computing](https://www.youtube.com/watch?v=H8bmHU_z8Ac&t=662s)
* [base2 genomics presentation for AWS re:invent](https://www.youtube.com/watch?v=8dApnlJLY54&t=2785s)

### To Do
* get jobs to write to different directories within the 1TB `docker_scratch` directory
* set up AMI that can be ssh'd into
* ~~run cellranger mkfastq and count on tiny-bcl as AWS batch job~~
* ~~save cellranger outputs back to S3 bucket~~
* ~~set up python script to actually run the cellranger commands~~
* ~~test running jobs with higher memory requirements, we need about 30-60GB~~
