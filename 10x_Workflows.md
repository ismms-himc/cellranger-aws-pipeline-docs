# 10x Workflows
This document proposes schemas and vocabulary to be used across: 
* [10x Technician Spreadsheets]: spreadsheets used by HIMC techs running assays
* [Processing-Run CSVs]: the computational team's pre-processing pipelines
* [Cell Ranger Required CSVs]: inputs to the Cell Ranger software
* [Output CSVs]: spreadsheets sent to end-users along with their data

Below are schemas and example data for various spreadsheets used by all parties, and [a glossary](#glossary) of relevant terms. This document heavily references the [10x documentation](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/using/mkfastq) as well.

## TODO
* look into [Multi-Library Sample workflow](https://support.10xgenomics.com/single-cell-vdj/software/pipelines/latest/advanced/multi-library-samples)
* look into potential [index hopping issues](https://community.10xgenomics.com/t5/10x-Idea-Exchange/Index-hopping-is-a-serious-problem-whose-effects-can-be/idi-p/68421)

## Examples from 10x Documentation
Below are two experimental scenarios from 10x that have been paraphrased into our vocabulary (see [Glossary]). 

### 2 Samples, 2 Libraries, 1 Seq-Run, 2 FBMs
[![Schematic of 2-sample, 1-seq-run workflow](https://support.10xgenomics.com/img/mkfastq-1.png "")](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/using/mkfastq#example_workflows)

> In this example, we have two 10x libraries (each processed through a separate Chromium chip channel) that are multiplexed on a single flowcell. Note that after running `cellranger mkfastq`, we run a separate instance of the pipeline on each library.

Note that library 2 is sequenced in two lanes and has two sets of lane-level FASTQs. Each sample has a Seq-Run FASTQ Set containing read and lane specificc FASTQs (see [Glossary]).

### 1 Sample, 1 Library, 2 Seq-Run, 1 FBM
[![Schematic of 1-sample, 2-seq-run workflow](https://support.10xgenomics.com/img/mkfastq-2.png "")](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/using/mkfastq#example_workflows)

> In this example, we have one 10x library sequenced on two flowcells. Note that after running cellranger mkfastq, we run a single instance of the pipeline on all the FASTQ files generated.

In this example a single library is sequenced twice (to get more reads per cell). Multiple sequencing runs of the same sample are the reason we are moving towards a Seq-Run FASTQ Set-level organization (rather than a library level only). 

## Default Example: 4-Sample Hashing CITE-seq Run

The spreadsheets produced in the following sections ([10x Technician Spreadsheets], [Processing-Run CSVs], [Cell Ranger Required CSVs], and [Output CSVs]) are based on the following default example: Four biological samples are hashed, ADTs are used to measure three surface markers, and the hashed sample is run on a single 10x chip lane (see [Example Experimental Scenarios] for examples with multiple chip lanes). The diagram below overviews the workflow from this processing run.

```
   Hash     Make         Pool       Seq Pooled  Demulti BCL   Calc FBM     De-hash 
   Samples  Libraries    Libraries  Library     (mkfastq)     (count/vdj)  Samples
   -------  -----------  ---------  ----------  ============  ===========  -------------
S1 -|        |-> L1-GEX   -|                     |-> FQ1-GEX  -|            |->  FBM1-S1 
S2 -|-> H1  -|-> L1-ADT   -|-> PL1   -> BCL1    -|-> FQ1-ADT  -|-> FBM1    -|->  FBM1-S2 
S3 -|        |-> L1-HTO   -|                     |-> FQ1-HTO  -|            |->  FBM1-S3 
S4 -|                                                                       |->  FBM1-S4 
```
Cell Ranger processing steps (`mkfastq`, `count`, `vdj`) are underlined with double underlines (`===`) and in this diagram make up the fifth and sixth steps. The final de-hashing step occurs independently of Cell Ranger in a post-processing Jupyter notebook. 

## 10X Technician Spreadsheets
Below are 4 proposed spreadsheets for use by the 10X techs and not all experiment-related columns are shown. 

### 1. Sample-Level Spreadsheet
| Sample Name | Loading Sample | Expected Cell Number | Ref Trans | Chemistry | HTO | Library Features | Cell Ranger Verison | Project |
|---|---|---|---|---|---|---|---|---|
| S1  | **H1** | 3000 | GRCh38 | 3p | HTO-1 | LF1 | 3.1.0 | P1 |
| S2  | **H1** | 4000 | GRCh38 | 3p | HTO-2 | LF1 | 3.1.0 | P1 |
| S3  | **H1** | 5000 | GRCh38 | 3p | HTO-3 | LF1 | 3.1.0 | P1 |
| S4  | **H1** | 6000 | GRCh38 | 3p | HTO-4 | LF1 | 3.1.0 | P1 |

#### Columns
- `Sample Name`: name of the biological sample being processed (see [Glossary])
- `Loading Sample`: name of the sample being loaded into the 10x chip that results in a set of partitioned single cells (a.k.a. GEM Group; see 10x glossary and [Glossary]). `Loading Sample` is the same as `Sample Name`, except in hashing experiments.
- `Expected Cell Number`: estimated number of cells in the loaded sample
- `Reference Transcriptome`: reference transcriptome that reads are aligned to, e.g. `GRCh38`
- `Chemistry`: name of the 10x kit chemistry being used (e.g. 5-prime); `3p` or `5p`
- `HTO`: name of the hash tag oligo (HTO) that is used to label this sample (`-` for a non-hashed sample)
- `Library Features`: links a sample to its list of features in the [Library Features Spreadsheet] (`-` if we are not measuring any ADTs or HTOs)
- `Cell Ranger Version`: software version we're using
- `Project`: project the sample is a part of

This spreadsheet shows four biological samples that are being hashed into a single loading sample (`H1`). Each sample is labeled with a different HTO (e.g. `HTO-1`) and share a common list of `Library Features` (i.e. all ADTs and HTOs used in the loading sample `H1`). `Loading Sample` links these samples to the `Library-Level Spreadsheet`, which lists all libraries derived from the loading sample `H1`. 

### 2. FASTQ-Level Spreadsheet
| FASTQs | Library  | Loading Sample | 10x Lane | Library Type | Hashed Sample | Sample Index | Pooled Library | BCL | To Output | Processing Run |
|---|---|---|---|---|---|---|---|---|---|---|
| FQ1-GEX | L1-GEX | H1 | XL1  | GEX  | True  | SI-GA-A3 | PL1 | **BCL1** | FBM1 | PR1 |
| FQ1-ADT | L1-ADT | H1 | XL1  | ADT  | True  |  RPI1    | PL1 | **BCL1** | FBM1 | PR1 |
| FQ1-HTO | L1-HTO | H1 | XL1  | HTO  | True  |  D7001   | PL1 | **BCL1** | FBM1 | PR1 |


- `FASTQs`: name of the Seq-Run-FASTQ Set that is the result of a single sequencing run.
  - Name includes: `Loading Sample`, `10x Lane ID`, `BCL Run ID`, `Library Type` (these examples leave off redundant information in the FASTQ names)
  - Tracking the `BCL` name allows us to handle the common scenario where the same pooled librry (e.g. tube of liquid) is 
- `Library`: **TODO**
- `Loading Sample`: **TODO**
- `10x Lane`: lane number a sample is loaded into, necessary for keeping track of a single sample being loaded into multiple lanes
- `Library Type`: type of library being prepared (e.g. GEX, ADT)
  - **TODO: we haven't decided whether chemistry and version may or may not be included, e.g. GEX_5-prime**
  - as far as I know, we can use Total-Seq antibodies to combine ADT and HTO data into the same library (I think the convention is to call these libraries `-AH`)
 - `Hashed Sample`: whether a loaded sample has been hashed
 - `Sample Index`: the index that is used to label the sequencing library when pooling a library into a pooled library. 
   - 10x GEX libraries have index names like `S1-GA-A3` (4 different oligos)
   - ADTs have `RPI` (single 6bp oligo)
   - HTOs have `D700` (single 8bp oligo)
- `Pooled Library`: the name of the pooled library (e.g. merged indexed libraries)
- `BCL`: name of the BCL file produced from sequencing the pooled library
- `To Output`: name of the output (e.g. feature barcode matrix, or VDJ contigs) a FASTQ is contributing to (e.g. `FBM1`, `TCR1`)
- `Processing Run`: the name of the ["processing run"][`Processing-Run`] (see [Glossary]) that the data is being organized under (i.e. all jobs necessary to convert BCL(s) into FBM(s) and TCR/VDJ output(s)).

This spreadsheet shows three Seq-Run-FASTQ Sets obtained by de-multiplexing `BCL1`. The spreadsheet shows which BCL the Seq-Run FASTQ set came from, which output it will contribute to (`FBM1`), and which processing run it is a part of (`PR1`). Note that the four biological samples from the [Sample-Level Spreadsheet] are not indicated in this table (this sample-level information will only be obtained after de-hashing after the Processing-Run).

Libraries (or Sequencing Libraries) are the result of running a `Loading Sample` through a 10x chip lane. The 10x techs must keep track of library-level information during the course of a run, however from the perspective of the computational team, these libraries play more of an intermediate role. In our example, we have three libraries (`L1-GEX`, `L1-ADT`, `L1-HTO`) that are generated from a single 10x chip lane. These libraries will be indexed, pooled into the pooled library (`PL1`) and sequenced to produce `BCL1` - note that additional sequencing runs can produce additional BCL files linked to the loading sample `H1`. The `BCL` column links the library to the `FASTQ-Level Spreadsheet` (one to many relationship, potentially).

### 3. Library Features Spreadsheet
| Library Features | HIMC Feature Name | Chemistry | Oligo ID | Oligo Sequence |  
|---|---|---|---|---|
| LF1 | HTO-1_H-101_3p_Lot# | 3p | H-101 | <unique-seq> |  
| LF1 | HTO-2_H-102_3p_Lot# | 3p | H-102 | <unique-seq> |  
| LF1 | HTO-3_H-103_3p_Lot# | 3p | H-103 | <unique-seq> |  
| LF1 | HTO-4_H-104_3p_Lot# | 3p | H-104 | <unique-seq> |  
| LF1 |   CD3_A-101_3p_Lot# | 3p | A-101 | <unique-seq> |  
| LF1 |   CD4_A-102_3p_Lot# | 3p | A-102 | <unique-seq> |  
| LF1 |   CD8_A-103_3p_Lot# | 3p | A-103 | <unique-seq> |  

#### Columns
- `Library Features`: this is the name of the list of features used in a library and is referenced in the [Sample-Level Spreadsheet].
- `HIMC Feature Name`: name of a feature (ADT or HTO) being measured
  - official gene symbol of the measured protein - ** might need to include species in name or lookup **
  - the unique HIMC oligo id (e.g. HIMC-1)
  - chemistry
  - the production lot number (e.g. lot-1) from the manufacturer
- `Chemistry`: the type of chemistry this feature is made for
- `Oligo ID`: the human readable name of the oligo used to label this feature
- `Oligo Sequence`: the actual oligo sequence   
 
This spreadsheet shows the list of `Library Features` that are associated with a loading sample (e.g. `H1`) and its subsequent sequencing libraries (`GEX`, `ADT`, `HTO`). This list is linked to samples in the [Sample-Level Spreadsheet].

## Processing-Run CSVs
A `Processing-Run` takes as input two spreadsheets and one or more BCLs. These two spreadsheets will be either produced using information from the [10x Technician Spreadsheets], either by the 10x-techs team or the computational team (possibly in an automated fashion). The two spreadsheets are similar to the required spreadsheets that `cellranger mkfastq` and `count` take as inputs, but also contain additional information (e.g. expected cell count) as well as an implicit layout of running all jobs required to complete a  `Processing-Run` set of jobs.

### 1. HIMC Sample Sheet

| FASTQs | From BCL | To Output | Seq-Lanes | Index Name | Index Oligo | Library Type | Ref Trans | Number of Cells | Chemistry | Cell Ranger Version | Library Features | Sample | Project | HTO |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **FQ1-GEX** | **BCL1** | **FBM1** | 1 | SI-GA-A3 | `-` | Gene Expression | GRCh38 | 18000 | 5p-V2 | 3.1.0 | LF1 | S1 | P1 | HTO1 |
| **FQ1-ADT** | **BCL1** | **FBM1** | 1 | RPI1 | ACTGTT | Custom | GRCh38 | 18000 | 5p-V2 | 3.1.0 | LF1 | S1 | P1 | HTO1 |
| **FQ1-HTO** | **BCL1** | **FBM1** | 1 | D7001 | ACTGTTGG | Custom | GRCh38 | 18000 | 5p-V2 | 3.1.0 | LF1 | S1 | P1 | HTO1 |

#### Columns

- `FASTQs`: name of the [Seq-Run-FASTQ set] obtained from the [FASTQ-Level Spreadsheet] which includes:
  - **biological sample name** (needed to track which sample FBM should be generated from which FASTQs)
  - **BCL file name** (needed to relate [Seq-Run-FASTQ sets][Seq-Run-FASTQ set] to specific BCL files)
- `From BCL`: name of the BCL file the FASTQs will be put into **or** some short-hand ID
- `To Output`: name of the output (e.g. feature barcode matrix, or VDJ contigs) a FASTQ is contributing to (e.g. `FBM1`, `TCR1`)
- `Seq-Lanes`: sequencing lanes used (comma-delimited)
- `Index Name`: human readable name of the `Sample Index` obtained from the [FASTQ-Level Spreadsheet]
- `Index Oligo`: actual index oligo sequence obtained from the Sample Index Spreadsheet (**TODO: not documented yet**); will be `-` for GEX index oligos since Cell Ranger `mkfastq` knows the meaning the index names (e.g. `SI-GA-3`).
- `Library Type`: the library type using the terminology acceptable to Cell Ranger Count (i.e. `Antibody Capture`, `Custom`, etc.; see [docs](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/using/feature-bc-analysis))
- `Reference Transcriptome`: reference transcriptome used for alignment
- `Number of Cells`: number of expected cells
- `Chemistry`: 10x kit chemistry version
    - note Cell Ranger takes specific chemistry names (see https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/using/count)
- `Cell Ranger Version`: version of the software to use
- `Library Features`: links a sample to its list of features in the [Library Features Spreadsheet]. The value is `-` if we are not measuring any ADTs or HTOs
- `Sample Name`: name of the biological sample being processed (see [Glossary])
- `Project`: project the sample is a part of
- `HTO`: name of the hash tag oligo (HTO) that is used to label this sample (`-` for a non-hashed sample)

This CSV is similar to the simple CSV sample sheet passed to `mkfastq`, but includes additional information required to perform multiple jobs within a Processing Run (e.g. multiple `mkfastq` and `count` jobs). This CSV will be used to construct both [the sample sheet CSV inputs for multiple `mkfastq` runs][10X Sample Sheet CSV] and [the library CSVs for multiple `count` runs][10X Libraries CSV]. The `Reference Transcriptome` and `Number of Cells` columns will be used to construct additional arguments for `cellranger count`. Additionally, the `Index Name` value will be used for GEX libraries, while the `Index Oligo` value will be used for Custom libraries (ADT/HTO).

**Note:** for all rows in the `HIMC Feature Reference CSV` file, the value for the column `feature_type` can be set to `Custom` only. It is not necessary that any other row exists with the value `Antibody Capture` or `Gene Expression` in this column.

### 2. HIMC Feature Reference CSV 

| Library Features | id | name | read | pattern | sequence | feature_type | 
|---|---|---|---|---|---|---|
| LF1 | HTO-1_H-101_3p_Lot# | HTO-1 | R2  | seq-pattern  | AACAAGACCCTTGAG  | Custom  |  
| LF1 | HTO-2_H-101_3p_Lot# | HTO-2 | R2  | seq-pattern  | CCCTTGAGAACAAGA  | Custom  |  
| LF1 | HTO-3_H-101_3p_Lot# | HTO-3 | R2  | seq-pattern  | AACATTGAGACCCAG  | Custom  |  
| LF1 | HTO-4_H-101_3p_Lot# | HTO-4 | R2  | seq-pattern  | TGAAACAAGACCCTG  | Custom  |  
| LF1 |   CD3_A-101_3p_Lot# |   CD3 | R2  | seq-pattern  | AACAACTTGAGGACC  | Custom  |  
| LF1 |   CD4_A-102_3p_Lot# |   CD4 | R2  | seq-pattern  | GGACCAAACAACTTG  | Custom  |  
| LF1 |   CD8_A-103_3p_Lot# |   CD8 | R2  | seq-pattern  | GGACCACTTGAACAA  | Custom  |  

#### Columns
- `Library Features`: name of the list of features used in a library
- `id`: unique id for the feature (can't collide with gene name)
- `name`: human readable feature name (e.g. gene name, or hashtag number HTO-1)
- `read`: specifies which sequencing read contains the sequence (e.g. R2)
- `pattern`: specifies how to extract seq from read
- `sequence`: nucleotide barcode sequence associated with this feature (e.g. antibody barcode or scRNA protospacer sequence)
- `feature_type`: the type (e.g. Custom) from the list of acceptable feature types: `Custom` (preferred),  `Antibody Capture`,  or `CRISPR Guide Capture` (see [docs](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/using/feature-bc-analysis))
- (omitted columns )`target_gene_id`, `target_gene_name`: are optional CRISPR-specific columns that are not shown in the example above.

This spreadsheet is only necessary for CITE-seq runs. It contains information on all the features used in a sequencing library. The addition of the `Library Features` column enables us to encode multiple libraries with different feature lableing schemes into a single sequencing run. Similarly, this scheme allows us to combine GEX only libraries (not shown) with feature-barcoding (or CITE-seq) libraries. 

### Pseudocode Processing Run
This pseudocode describes how to set up a Processing Run using the [HIMC Sample Sheet]:

```
# load sample sheet
df_ss = pd.read_csv('proc_run_csvs/himc_sample_sheet.csv')

# load feature ref if necessary
if df_fl exists:
    df_fl = pd.read_csv('proc_run_csvs/feature_ref.csv')

# find all bcl files
all_bcl <= df_ss

# find all outputs
all_outs <= df_ss

# keep track of all job ids
jobs = {}

# run mkfastq for each bcl, pass in meta_data
for inst_bcl in all_bcl:
    jobs[inst_bcl] = submit_mkfastq(inst_bcl, inst_meta_data)

# run count/vdj for each output, pass in meta_data
for inst_out in all_outs:
    
    # find all required FASTQs for job
    (look up in df_ss)
    
    # find dependent bcl
    (look up in df_ss)
    
    # find feature list if necessary
    (find inst_fl)
    
    # submit job with dependent bcl job
    if inst_out == 'fbm':
        jobs[inst_out] = submit_count(inst_out, jobs[dep_bcl], inst_fl, inst_meta_data)
    elif inst_out == 'vdj':
        jobs[inst_out] = submit_vdj(inst_out, jobs[dep_bcl], inst_meta_data)
```

## Cell Ranger Required CSVs

### 1. Sample Sheet CSV
| Lane| Sample | Index |
|---|---|---|
| 1  | FQ1-GEX | SI-GA-A3 |
| 1  | FQ1-ADT | ACTGTT |
| 1  | FQ1-HTO | ACTGTTGG |

#### Columns
- `Lane`: which lane(s) of the flowcell to process. Can be either a single lane, a range (e.g., 2-4) or '*' for all lanes in the flowcell.
- `Sample`: The name of the sample. This name will be the prefix to all the generated FASTQs, and will correspond to the `--sample` argument downstream 10x pipelines.
Sample names must conform to the Illumina `bcl2fastq` naming requirements. Only letters, numbers, underscores and hyphens area allowed; no other symbols, including dots (".") are allowed (the BCL name will be appended automatically by `mkfastq`; **TODO: verify this**).
- `Index` The 10x sample index set that was used in library construction, e.g., `SI-GA-A12`.
  - When processing custom oligos (e.g. ADTs/HTOs), pass the actual oligo sequences here.
 
This is the "simple samplesheet" format consumed by `cellranger mkfastq` (see 10x docs).

### Index sequence collision
If two or more index sequences are too close to each other (e.g., the distance is 2 or less bases), `cellranger mkfastq` calls an index sequence collision and exits with an error. The error message returned by `cellranger mkfastq` is written below:

```
The sample sheet supplied has a sample index collision. This can happen if the
same sample index and lane were specified for multiple samples, or in certain
cases where 10x Chromium i7 Multiplex Kit and i7 Multiplex Kit N samples were
run on the same flowcell. It is a known issue that certain sample index
combinations from these two different kits only differ by two bases-- meaning
that it is possible for the sequencer to generate index reads with sequences
that are one base away from multiple sample indices.
Please check your samplesheet to verify you do not have duplicate lane-sample
index pairs for multiple samples. If there are no duplicates, please run
mkfastq with a --barcode-mismatches=0 argument. (The default parameter is
--barcode-mismatches=1). This will make bcl2fastq only accept reads that
match the sample indices exactly. The small percentage of reads that are a
single base away from multiple sample indices will be ignored.
```

There are two ways to solve this collision. One is to set the parameter `--barcode-mismatches` to 0 (`--barcode-mismatches=0`). This is a `bcl2fastq` parameter, so it is not documented on the 10x Cellranger documentation; however, this parameter can be passed to `cellranger mkfastq`. For more information, please refer to the [`bcl2fastq`](https://support.illumina.com/content/dam/illumina-support/documents/documentation/software_documentation/bcl2fastq/bcl2fastq2-v2-20-software-guide-15051736-03.pdf) documentation. The second way is to run `cellranger mkfastq` separately for each sequencing library (potentially in a different container), even though they are all in the same BCL file. This way, each execution of `cellranger mkfastq` generates the Seq-Run-FASTQ Set for a single sequencing library and is unaware of the rest of sequencing libraries, so that index sequence collisions are not called.

### Multiple `cellranger mkfastq` processes writing on the same directory  

Occasionally, multiple `cellranger mkfastq` processes running on the same machine can attempt to write on the same directory. These processes can be spawned from the same call to `cellranger mkfastq`. When a `cellranger mkfastq` process attempts to write on a directory, it checks the file `<mkfastq_dir>/_lock`, where `<mkfastq_dir>` is the directory created by `cellranger mkfastq`. Ocassionally, if this file is created by other process, then the running process cannot write on the directory and returns an error. This is a concurrency error that, to the best of our knowledge, has not been solved by 10x. Since it is non-deterministic, the same command `cellranger mkfastq` can be executed with the same parameters until it finishes without errors. More information can be found [here](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/troubleshooting).

### 2. Libraries CSV
|  FASTQs | Sample  |  Library Type |
|---|---|---|
| /path/to/fastqs/ | FQ1-GEX | Gene Expression |
| /path/to/fastqs/ | FQ1-ADT | Custom |
| /path/to/fastqs/ | FQ1-HTO | Custom |

#### Columns
- `FASTQs`: path to demultiplexed FASTQ files (cannot have comma-delimiited paths; more than one path requres an additional row).
- `Sample`: sample name assigned in the `mkfastq` simple samplesheet above.
- `Library Type`: from the documentation:
  > The FASTQ data will be interpreted using the rows from the feature reference file that have a ‘feature_type’ that matches this library_type. This field is case-sensitive, and must match a valid library type as described in the Library / Feature Types section. Must be Gene Expression for the gene expression libraries. Must be one of Custom, Antibody Capture, or CRISPR Guide Capture for Feature Barcoding libraries.

This table is used by Cell Ranger Count to know which `FBM-FASTQ Set` (which is composed of at least one `Seq-Run-FASTQ Sets` from different sequencing runs, see [Glossary]) to aggregate into a single FBM, which includes GEX, ADT, and HTO data.

### 3. Feature Reference CSV

This is the same as the [Feature Reference CSV] that is produced by the 10x techs, but without the column `Library Features`. 

## Output CSVs
A single processing run will produce the following spreadsheets:
1. Job Status CSV
2. FASTQ meta-data
3. Outputs Meta-Data CSV

### 1. Job Meta-Data CSV

| Job  | Status  | Job Dependencies | Output Path  | 
|---|---|---|---|
| mkfastq_BCL1  | Finished   | - | s3/path/to/zipped/fastqs  | 
| count_FBM1  | Pending Job  | [mkfastq_BCL1] | s3/path/to/fbm  |

#### Columns
- `Job`: the name of the job
  - `mkfastq` jobs' names will include the input BCL name
  - `count` jobs' names will include the output FBM name
  - `vdj` jobs' names will include the output TCR/BCR name
- `Status`: current status of the job: 
   - `Not Submitted`: has not been submitted for running
   - `Pending Data`: a `mkfastq` job that is waiting on `bcl` data
   - `Pending Job`: a `count` or `vdj` job that is waiting on the completion of a dependent job (e.g. a `count` run waiting on the completion of a `mkfastq` run)
   - `In-Progress`: a job that is currently running
   - `Finished`: a successfully completed job
   - `Failed`: a job that has failed (does not include informaiton on why it failed)
   
- `Job Dependencies`: a list of all dependent jobs (e.g. jobs that need to be completed before this job runs
- `Output Path`: S3 path to the FASTQs, FBM, or TCR/BCR (we may drop this column when we share with researchers, but it is good for internal use)

This spreadsheet shows the status of the jobs associated with a single Processing-Run. This spreadsheet serves two purposes: 

1) Provide the 10x techs and computational teams with a simple way of checking the status of a Processing Run
2) Provide the pipeline a way to access the state of the Processing Run. For instance, it is a common scenario to receive multiple BCLs from the same sample (e.g. multiple sequencing runs) and we will need to start processing (e.g. get the number of reads from the FASTQs) before we obtain all BCLs. We would like to be able to add additional BCLs to a Processing-Run bucket and tell the Processing-Run job to complete the necesssary jobs that are available to complete. 

### 2. FASTQ Meta-Data CSV
This spreadsheet will be a modified copy of [the FASTQ-level sheet][FASTQ-Level Spreadsheet] that is used as input to a Processing-Run. We will add the following columns: 

- `reads per cell`: obtained from `mkfastq` QC metrics 
- `Download Link`: a pre-signed URL for downloading the FASTQs from S3

### 3. Outputs Meta-Data CSV

| Outputs  | Path  | Download Link | Number of Cells |
|---|---|---|---|
| FBM1  |  s3/path/to/zipped/fastqs  | URL | 10000 | 

#### Columns
- `Outputs`: name of the FBM or VDJ outputs
- `Path`: path on the S3 bucket to the FASTQs (we may drop this column when we share with researchers, but it is good for internal use)
- `Download Link`: a pre-signed URL for downloading the outputs
- `Number of Cells`: number of cells (based on 10x filtering)

This will give meta-data on FBM/VDJ outputs. For a hashed sample, we will have to perform de-hashing (**TODO: document this process**) to get the individual samples from the hashed loading sample (otherwise they are 1-to-1).

## Example Experimental Scenarios
This section enumerates experimental scenarios of increasing complexity including::
- multiple samples in Processing Run
- multiple rounds of sequencing per sample
- multiple 10x chip lanes per sample
- TCR/BCR sequencing
- Hashtagging and ADT measurement

Each scenario includes a workflow diagram as well as a simplified [HIMC Sample Sheet]. The simplified sample sheet shows where each Seq-Run FASTQ Set originated (`From BCL`) and what output the Seq-Run FASTQ Set contributes towards (`To Output`), which should be sufficient for organizing multiple runs of `mkfastq` and `count`, respectively, within the larger context of a complete Processing Run (additional meta-data necessary for a Processing Run can be found in the [HIMC Sample Sheet]). 

### 1. Single Lane per Sample, Single Seq-Run
```
 Make        Make Pooled   Seq Pooled    Demulti     Calc
 Libraries   Library       Library       BCL         FBMs
 ---------   ---------     -------       ====        ====
S1   ->   L1    -|                        |->   FQ1   ->  FBM1
S2   ->   L2    -|->   PL1   ->   BCL1   -|->   FQ2   ->  FBM2
S3   ->   L3    -|                        |->   FQ3   ->  FBM3
```
| FASTQs | From BCL | To Output |
|---|---|---|
| FQ1 | BCL1 | FBM1 |
| FQ2 | BCL1 | FBM2 |
| FQ3 | BCL1 | FBM3 |

Three samples are run in three 10x chip lanes producing three GEX libraries. A pooled library is generated and sequenced once. The BCL file is de-multiplexed into three sets of Seq-Run FASTQ Sets and each is run in a separate instance of Cell Ranger Count to produce three FBMs. 

### 2. Single Lane per Sample, Multiple Seq-Runs 
```
 Make        Make Pooled   Seq Pooled    Demulti        Calc
 Libraries   Library       Library       BCLs           FBMs
 ---------   ---------     -------       ====           ====
                                         |->  FQ1-BCL1  -|->  FBM1
                                         |->  FQ1-BCL2  -|
S1   ->   L1   -|           |->   BCL1  -| 
S2   ->   L2   -|->   PL1  -|            |->  FQ2-BCL1  -|->  FBM2
S3   ->   L3   -|           |->   BCL2  -|->  FQ2-BCL2  -|
                                         |
                                         |->  FQ3-BCL1  -|->  FBM3
                                         |->  FQ3-BCL2  -|
```
| FASTQs | From BCL | To Output |
|---|---|---|
| FQ1-BCL1 | BCL1 | FBM1 |
| FQ1-BCL2 | BCL2 | FBM1 |
| FQ2-BCL1 | BCL1 | FBM2 |
| FQ2-BCL2 | BCL2 | FBM2 |
| FQ3-BCL1 | BCL1 | FBM3 |
| FQ3-BCL2 | BCL2 | FBM3 |

Three samples are run in three 10x chip lanes producing three GEX libraries. A pooled library is generated and sequenced twice in order to get more reads per cell. The BCL files are de-multiplexed into six sets of Seq-Run FASTQ Sets (note that FASTQs need their BCL name in order to be unique). Three runs fo Cell Ranger count are run on the three FBM FASTQ Sets (each set is composed of two Seq-Run FASTQ Sets, note reordering of FASTQs in the diagram) to produce three FBMs. 

### 3. Multiple Lanes per Sample, Single Seq-Run

```
  Make           Make Pooled   Seq Pooled    Demulti         Calc
  Libraries      Library       Library       BCL             FBMs
  ---------      ---------     -------       ====            ====
S1   -|-> L1-XL1    -|                        |->   FQ1-XL1   ->  FBM1-XL1
      |-> L1-XL2    -|                        |->   FQ1-XL2   ->  FBM1-XL2
                     |                        |
S2   -|-> L2-XL3    -|->   PL1   ->   BCL1   -|->   FQ2-XL3   ->  FBM2-XL3
      |-> L2-XL4    -|                        |->   FQ2-XL4   ->  FBM2-XL4
                     |                        |
S3   -|-> L3-XL5    -|                        |->   FQ3-XL5   ->  FBM3-XL5
      |-> L3-XL6    -|                        |->   FQ3-XL6   ->  FBM3-XL6
```
| FASTQs | From BCL | To Output |
|---|---|---|
| FQ1-XL1 | BCL1 | FBM1-XL1 |
| FQ1-XL2 | BCL1 | FBM1-XL2 |
| FQ2-XL3 | BCL1 | FBM2-XL3 |
| FQ2-XL4 | BCL1 | FBM2-XL4 |
| FQ3-XL5 | BCL1 | FBM3-XL5 |
| FQ3-XL6 | BCL1 | FBM3-XL6 |

Three samples are run in two 10x chip lanes each (to double the number of measured cells) producing six GEX libraries. A pooled library is generated and sequenced once. The BCL file is de-multiplexed into six sets of Seq-Run FASTQ Sets. Six runs of Cell Ranger count are run on the six FBM FASTQ Sets. Note that in this scenario, we are leaving it to the user to combine data from different lanes (e.g. different samples of cell from the same biological sample) of the same subject (e.g. `FBM1-XL1` and `FBM1-XL2`).

### 4. Multiple Lanes per Sample, Multiple Seq-Runs
```
  Make           Make Pooled      Seq Pooled  Demulti              Calc
  Libraries      Library          Library     BCLs                 FBMs
  ---------      ---------        -------     ====                 ====
      |-> L1-XL1    -|                        |->   FQ1-XL1-BCL1   -|->  FBM1-XL1
S1   -|              |                        |->   FQ1-XL1-BCL2   -|  
      |              |                        |
      |-> L1-XL2    -|                        |->   FQ1-XL2-BCL1   -|->  FBM1-XL2
                     |                        |->   FQ1-XL2-BCL2   -|  
                     |                        |  
      |-> L2-XL3    -|            |-> BCL1   -|->   FQ2-XL3-BCL1   -|->  FBM2-XL3
S2   -|              |->   PL1   -|           |->   FQ2-XL3-BCL2   -|    
      |              |            |-> BCL2   -|
      |-> L2-XL4    -|                        |->   FQ2-XL4-BCL1   -|->  FBM2-XL4
                     |                        |->   FQ2-XL4-BCL2   -|    
                     |                        |
      |-> L3-XL5    -|                        |->   FQ3-XL5-BCL1   -|->  FBM3-XL5
S3   -|              |                        |->   FQ3-XL5-BCL2   -|    
      |              |                        |                     
      |-> L3-XL6    -|                        |->   FQ3-XL6-BCL1   -|->  FBM3-XL6
                     |                        |->   FQ3-XL6-BCL2   -|    
```
| FASTQs | From BCL | To Output |
|---|---|---|
| FQ1-XL1-BCL1 | BCL1 | FBM1-XL1 |
| FQ1-XL1-BCL2 | BCL2 | FBM1-XL1 |
| FQ1-XL2-BCL1 | BCL1 | FBM1-XL2 |
| FQ1-XL2-BCL2 | BCL2 | FBM1-XL2 |
| FQ2-XL3-BCL1 | BCL1 | FBM2-XL3 |
| FQ2-XL3-BCL2 | BCL2 | FBM2-XL3 |
| FQ2-XL4-BCL1 | BCL1 | FBM2-XL4 |
| FQ2-XL4-BCL2 | BCL2 | FBM2-XL4 |
| FQ3-XL5-BCL1 | BCL1 | FBM3-XL5 |
| FQ3-XL5-BCL2 | BCL2 | FBM3-XL5 |
| FQ3-XL6-BCL1 | BCL1 | FBM3-XL6 |
| FQ3-XL6-BCL2 | BCL2 | FBM3-XL6 |

Three samples are run in two 10x chip lanes each (to double the number of measured cells) producing six GEX libraries. A pooled library is genrated and sequenced twice (to get more reads per cell). The BCL files are de-multiplexed into twelve sets of Seq-Run FASTQ Sets and six corresponding FBM FASTQ Sets. Six runs of Cell Ranger `count` are run on the six FBM FASTQ Sets. 
This example has multiple lanes per sample to get more cells per sample and multiple reads per sample to get more reads per cell. Similarly to scenario 3, we are leaving it to the user to combine data from different lanes of the same subject. 

### 5. One Lane per Sample, TCR-seq, Single Seq-Run
```
  Make             Make Pooled   Seq Pooled     Demulti           Calc
  Libraries        Library       Library        BCL               FBM/VDJ
  ---------        ---------     -------        ====              ========
S1   -|->   L1-GEX    -|->   PL1   -|->   BCL1  ->  FQ1-BCL1-GEX    ->   FBM1  
      |->   L1-TCR    -|            |->   BCL2  ->  FQ1-BCL2-TCR    ->   TCR1  
```
| FASTQs | From BCL | To Output |
|---|---|---|
| FQ1-BCL1-GEX | BCL1 | FBM1 |
| FQ1-BCL2-TCR | BCL2 | TCR1 |

One sample is run in a 10x chip lane producing one GEX library and one TCR library. A pooled library is generated and sequenced twice (once for GEX and once for VDJ). The BCL files are 'de-multiplexed' into a single set of Seq-Run FASTQ Set per BCL (`FQ1-GEX1` and `FQ1-TCR`). Cell Ranger `count`/`vdj` are run on `FQ1-GEX1`/`FQ1-TCR` respectively to produce outputs (FBM/contigs). Note that two sequencing runs are performed on the pooled sample because sequencing conditions are different for GEX and VDJ.

### 6. Multiple Lanes per Sample, TCR-seq, BCR-seq, Multiple Seq-Run
```
  Make                 Make Pooled   Seq Pooled     Demulti               Calc
  Libraries            Library       Library        BCL                   FBM/VDJ
  ---------            ---------     -------        ====                  ========
      |->   L1-XL1-GEX    -|            |->   BCL1  -|->  FQ1-XL1-BCL1-TCR    ->   TCR1-XL1
S1   -|->   L1-XL1-TCR    -|            |            |->  FQ1-XL1-BCL1-BCR    ->   BCR1-XL1
      |->   L1-XL1-BCR    -|->   PL1   -|
      |                    |            |            |->  FQ1-XL1-BCL2-GEX    ->   FBM1-XL1
      |->   L1-XL2-GEX    -|            |->   BCL2  -|->  FQ1-XL2-BCL2-GEX    ->   FBM1-XL2
```
| FASTQs | From BCL | To Output |
|---|---|---|
| FQ1-XL1-BCL1-TCR | BCL1 | TCR1-XL1 |
| FQ1-XL1-BCL1-BCR | BCL1 | BCR1-XL1 |
| FQ1-XL1-BCL2-GEX | BCL2 | FBM1-XL1 |
| FQ1-XL2-BCL2-GEX | BCL2 | FBM1-XL2 |

One sample is run in two lanes. One lane includes TCR and BCR sequencing (`XL1`) and the other includes GEX only (`XL2`). A pooled library is generated and sequenced two times (once for GEX and once for VDJ). The BCL files are de-multiplexed. Cell Ranger `count` and `vdj` are run for thier respective FASTQs. 

### 7. One Lane per Sample, ADT, Single Seq-Run
```
 Make           Make Pooled   Seq Pooled    Demulti         Calc
 Libraries      Library       Library       BCL             FBMs
 ---------      ---------     -------       ====            ====
S1   -|->  L1-GEX  -|                        |->  FQ1-GEX  -|->  FBM1
      |->  L1-ADT  -|                        |->  FQ1-ADT  -|
                    |                        |
S2   -|->  L2-GEX  -|->   PL1   ->   BCL1   -|->  FQ2-GEX  -|->  FBM2
      |->  L2-ADT  -|                        |->  FQ2-ADT  -|
                    |                        |
S3   -|->  L3-GEX  -|                        |->  FQ3-GEX  -|->  FBM3
      |->  L3-ADT  -|                        |->  FQ3-ADT  -|
```
| FASTQs | From BCL | To Output |
|---|---|---|
| FQ1-GEX | BCL1 | FBM1 |
| FQ1-ADT | BCL1 | FBM1 |
| FQ2-GEX | BCL1 | FBM2 |
| FQ2-ADT | BCL1 | FBM2 |
| FQ3-GEX | BCL1 | FBM3 |
| FQ3-ADT | BCL1 | FBM3 |

Three ADT samples are run in three lanes producing three GEX and three ADT libraries. These libraries are pooled and sequenced once. The BCL file is de-multiplexed into six Seq-Run FASTQ Sets and three FBM FASTQ Sets (each containing GEX and ADT FASTQs). Cell Ranger `count` (using feature barcoding) is run three times to produce three FBMs containing both GEX and ADT data. 

### 8. One Lane per Sample, ADT, Multiple Seq-Run
```
 Make           Make Pooled   Seq Pooled    Demulti            Calc
 Libraries      Library       Library       BCL                FBMs
 ---------      ---------     -------       ====               ====
      |->  L1-GEX  -|                        |->  FQ1-BCL1-GEX  -|
S1   -|             |                        |->  FQ1-BCL2-GEX  -|->  FBM1
      |->  L1-ADT  -|                        |->  FQ1-BCL1-ADT  -|
                    |                        |->  FQ1-BCL2-ADT  -|      
                    |                        |
S2   -|->  L2-GEX  -|            |->  BCL1  -|->  FQ2-BCL1-GEX  -|
      |             |->   PL1   -|           |->  FQ2-BCL2-GEX  -|->  FBM2
      |->  L2-ADT  -|            |->  BCL2  -|->  FQ2-BCL1-ADT  -|
                    |                        |->  FQ2-BCL2-ADT  -|
                    |                        |
S3   -|->  L3-GEX  -|                        |->  FQ3-BCL1-GEX  -|
      |             |                        |->  FQ3-BCL2-GEX  -|->  FBM3
      |->  L3-ADT  -|                        |->  FQ3-BCL1-ADT  -|
                                             |->  FQ3-BCL2-ADT  -|      
```
| FASTQs | From BCL | To Output |
|---|---|---|
| FQ1-BCL1-GEX | BCL1 | FBM1 |
| FQ1-BCL2-GEX | BCL2 | FBM1 |
| FQ1-BCL1-ADT | BCL1 | FBM1 |
| FQ1-BCL2-ADT | BCL2 | FBM1 |
| FQ2-BCL1-GEX | BCL1 | FBM2 |
| FQ2-BCL2-GEX | BCL2 | FBM2 |
| FQ2-BCL1-ADT | BCL1 | FBM2 |
| FQ2-BCL2-ADT | BCL2 | FBM2 |
| FQ3-BCL1-GEX | BCL1 | FBM3 |
| FQ3-BCL2-GEX | BCL2 | FBM3 |
| FQ3-BCL1-ADT | BCL1 | FBM3 |
| FQ3-BCL2-ADT | BCL2 | FBM3 |

Three biological samples are run in three lanes producing three GEX and three ADT libraries. These libraries are pooled and sequenced twice. The BCL files are de-multiplexed into twelve Seq-Run FASTQ Sets and three FBM FASTQ Sets (each containing GEX and ADT FASTQs). Cell Ranger `count` (using feature barcoding) is run three times to produce three FBMs containing both GEX and ADT data. 

### 9. Hashed-ADT, One Lane per Sample, Single Seq-Run
```
 Hash      Make             Pool        Seq Pooled   Demulti       Calc       De-hash 
 Samples   Libraries        Libraries   Library      BCL           FBM        Samples
 -------   ---------        ---------   ---------    ====          ====       --------
S1 -|          |->   L1-GEX   -|                     |->  FQ1-GEX  -|           |->  FBM1-S1 
S2 -|->  H1   -|->   L1-ADT   -|->   PL1  ->  BCL1  -|->  FQ1-ADT  -|->  FBM1  -|->  FBM1-S2 
S3 -|          |->   L1-HTO   -|                     |->  FQ1-HTO  -|           |->  FBM1-S3 
S4 -|                                                                           |->  FBM1-S4 
```
| FASTQs | From BCL | To Output |
|---|---|---|
| FQ1-GEX | BCL1 | FBM1 |
| FQ1-ADT | BCL1 | FBM1 |
| FQ1-HTO | BCL1 | FBM1 |

This is the same as the default example used earlier in the documentation. Four ADT samples are hashed into a single Loading Sample (`H1`) and run in a single 10x lane, which generates three libraries. The libraries are pooled and sequenced once. The BCL files are de-multiplexed into three Seq-Run FASTQ Sets and one FBM FASTQ Set. Cell Ranger `count` (using feature barcoding) is run once to produce one FBM containing GEX, ADT, and HTO data. De-hashing is manually run after the Processing Run to obtain sample level FBMs. 

### 10. Hashed-ADT, Multiple Lanes per Sample, ADT, Single Seq-Run
```
 Hash      Make             Pool         Seq Pooled     Demulti           Calc       De-hash 
 Samples   Libraries        Libraries    Library        BCL               FBM        Samples
 -------   ---------        ---------    ---------      ====              ====       --------
              |->   L1-XL1-GEX   -|                     |->  FQ1-XL1-GEX  -|           |->  FBM1-S1 
              |->   L1-XL1-ADT   -|                     |->  FQ1-XL1-ADT  -|->  FBM1  -|->  FBM1-S2 
              |->   L1-XL1-HTO   -|                     |->  FQ1-XL1-HTO  -|           |->  FBM1-S3 
S1 -|         |                   |                     |                              |->  FBM1-S4 
S2 -|->  H1  -|                   |->   PL1  ->  BCL1  -|
S3 -|         |                   |                     |
S4 -|         |->   L1-XL2-GEX   -|                     |->  FQ1-XL2-GEX  -|           |->  FBM2-S1 
              |->   L1-XL2-ADT   -|                     |->  FQ1-XL2-ADT  -|->  FBM2  -|->  FBM2-S2 
              |->   L1-XL2-HTO   -|                     |->  FQ1-XL2-HTO  -|           |->  FBM2-S3 
                                                                                       |->  FBM2-S4 
```
| FASTQs | From BCL | To Output |
|---|---|---|
| FQ1-XL1-GEX | BCL1 | FBM1 |
| FQ1-XL1-ADT | BCL1 | FBM1 |
| FQ1-XL1-HTO | BCL1 | FBM1 |
| FQ1-XL2-GEX | BCL1 | FBM2 |
| FQ1-XL2-ADT | BCL1 | FBM2 |
| FQ1-XL2-HTO | BCL1 | FBM2 |

Four ADT samples are hashed into a single Loading Sample (`H1`) and run in two 10x lanes (to get more cells), which generates six libraries. The libraries are pooled and sequenced once. The BCL files are de-multiplexed into six Seq-Run FASTQ Sets and two FBM FASTQ Set. Cell Ranger `count` (using feature barcoding) is run twice to produce two FBMs containing GEX, ADT, and HTO data. De-hashing is manually run twice after the Processing Run to obtain sample level FBMs. 

## Glossary

The relationships between components in 10x single cell assay can be complicated. As a first step, we define a common vocabulary for ourselves below. We have ordered entities based on their natural progression during the experiment and data-processing steps.  

* **BCL File**: contains sequencing information on a pooled library (e.g. set of multiplexed sequencing libraries).

* **Biological Sample**: a cell suspension extracted from a single biological source, see [10x-Glossary](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/glossary).

* **Cell Ranger Output**: The set of outputs from Cell Ranger `count` or `vdbj`. For `count` the outputs include a feature barcode matrix (FBM) which can be the product of several sequencing runs and BCL files. For `vdj` the outputs include TCR/BCR contigs.

* **FASTQ**: the product(s) of de-multiplexing BCL files.

* **FBM-FASTQ Set**: a set of FASTQs that will be used to generate a single FBM (feature barcode matrix). If the same pooled library is sequenced multiple times (producing multiple BCL files) we will need to combine multiple Seq-Run-FASTQ sets (see above) into a single FBM.

* **GEM Group**: A set of partitioned cells (Gelbeads-in-Emulsion) from a single 10x Chromium™ Chip channel. One or more sequencing libraries can be derived from a GEM Group.

* **Loading Sample**: the sample loaded into a 10x lane, which is usually the biological sample but may be a hash of many biological samples.

* **Library Features List**: A list of features used in a library. The list will have a name like `LF1` in this documentation and the list includes all relevant hashtag and antibody features. 

* **Pooled Library**: a combination of several indexed sequencing libraries (from several 10x chip lanes) for loading into a sequencer and obtaining a BCL file.

* **Processing-Run**: a set of cellranger `mkfastq`, `count`, and `vdj` (if applicable) runs that take as input: 1) one or more BCL files and 2) Processing-Run Input CSV files. The Processing-Run produces the following outputs: 1) FASTQs, 2) FBMs (feature barcode matrices) and if applicable TCR/BCR data, 3) [Processing-Run Status CSV] which lists out all jobs in the Processing-Run as well as where to find outputs 4) [Processing-Run Meta-Data CSV] relevant metadata (still being sorted out) for 10x techs.

* **Project**: A research project involving multiple biological samples. Our goal is to arrange sample-level data into parent project directories. 

* **Sample-Level Outputs**: FBMs and VDJ data that has been re-organized into sample level data. This usually consists of copying sample level data out of the Processing Run, but for hashing runs requires manual de-hashing (post-Cell Ranger step).

* **Seq-Run-FASTQ Set**: a set of FASTQs that have been de-multiplexed from a single BCL file that give data for a single indexed sequencing library (e.g. a single GEX or ADT library). This set consists of lane- and read-specific FASTQs. 

* **Library (Sequencing Library)**: the end product(s) from a 10x chip lane. A single 10x lane can produce a single (e.g. GEX) or multiple sequencing libraries (e.g. GEX and VDJ; or GEX, ADT, and HTO). These sequencing libraries will either be pooled into a single pooled library and sequenced or run on separate sequencing runs (e.g. as is the case for VDJ and GEX which require different sequencing conditions).

[Glossary]: #glossary
[10x Technician Spreadsheets]: #10x-technician-spreadsheets
[Processing-Run CSVs]: #processing-run-csvs
[Cell Ranger Required CSVs]: #cell-ranger-required-csvs
[Output CSVs]: #output-csvs
[Feature Reference CSV]: #feature-reference-csv
[Library Features Spreadsheet]: #3-library-features-spreadsheet
[`Processing-Run`]: #processing-run-spreadsheets
[10X Sample Sheet CSV]: #1-sample-sheet-csv
[10X Libraries CSV]: #2-libraries-csv
[Processing-Run Status CSV]: #1-processing-run-status-csv
[Processing-Run FASTQ Meta-Data CSV]: #2-processing-run-fastq-meta-data-csv
[Processing-Run Sample Meta-Data CSV]: #3-processing-run-sample-meta-data-csv
[Sample-Level Spreadsheet]: #1-sample-Level-spreadsheet
[FASTQ-Level Spreadsheet]: #2-fastq-Level-spreadsheet
[Features Table]: #4-features-table
[HIMC Sample Sheet]: #1-himc-sample-sheet
[Seq-Run-FASTQ set]: TODO
[Example Experimental Scenarios]: #Example-Experimental-Scenarios
