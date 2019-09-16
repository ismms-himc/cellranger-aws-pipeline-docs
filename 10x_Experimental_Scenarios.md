# 10x Experimental Scenarios
This document proposes schemas and vocabulary to be used across: 
* [10x Technician Spreadsheets]: spreadsheets used by HIMC techs running assays
* [Processing-Run CSVs]: the computational team's pre-processing pipelines
* [Cell Ranger Required CSVs]: the Cell Ranger software
* [Output CSVs]: spreadsheets sent to end-users along with their data

Below are schemas and example data for various spreadsheets used by all parties, and [a glossary](#glossary) of relevant terms. This document heavily references the [10x documentation](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/using/mkfastq) as well.

# Examples from 10x Documentation
Below are two experimental scenarios from 10x that have been paraphrased into our vocabulary (see [Glossary]). 

### 2 Samples, 2 Libraries, 1 Seq-Run, 2 FBMs
[![Schematic of 2-sample, 1-seq-run workflow](https://support.10xgenomics.com/img/mkfastq-1.png "")](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/using/mkfastq#example_workflows)

> In this example, we have two 10x libraries (each processed through a separate Chromium chip channel) that are multiplexed on a single flowcell. Note that after running `cellranger mkfastq`, we run a separate instance of the pipeline on each library.

Note that library 2 is sequenced in two lanes and has two sets of lane-level FASTQs. Each sample has a Seq-Run FASTQ Set containing read and lane specificc FASTQs (see [Glossary]).

### 1 Sample, 1 Library, 2 Seq-Run, 1 FBM
[![Schematic of 1-sample, 2-seq-run workflow](https://support.10xgenomics.com/img/mkfastq-2.png "")](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/using/mkfastq#example_workflows)

> In this example, we have one 10x library sequenced on two flowcells. Note that after running cellranger mkfastq, we run a single instance of the pipeline on all the FASTQ files generated.

In this example a single library is sequenced twice (to get more reads per cell). Multiple sequencing runs of the same sample are the reason we are moving towards a Seq-Run FASTQ Set-level organization (rather than a library level only). 

# Default Example: 4-Sample Hashing CITE-seq Run

The spreadsheets produced in the following sections ([10x Technician Spreadsheets], [Processing-Run CSVs], [Cell Ranger Required CSVs], and [Output CSVs]) are based on the following default example: Four biological samples are hashed, ADTs are used to measure three surface markers, and the hashed sample is run on a single 10x chip lane. The diagram below overviews the workflow from this processing run.

```
 Hash      Make             Pool        Seq Pooled   Demulti       Calc       De-hash 
 Samples   Libraries        Libraries   Library      BCL           FBM        Samples
 -------   ---------        ---------   ---------    =======       ====       --------
S1 -|          |->   L1-GEX   -|                     |->  FQ1-GEX  -|           |->  FBM1-S1 
S2 -|->  H1   -|->   L1-ADT   -|->   PL1  ->  BCL1  -|->  FQ1-ADT  -|->  FBM1  -|->  FBM1-S2 
S3 -|          |->   L1-HTO   -|                     |->  FQ1-HTO  -|           |->  FBM1-S3 
S4 -|                                                                           |->  FBM1-S4 
```
Cell Ranger processing steps (`mkfastq`, `count`, `vdj`) are underlined with double underlines (`===`) and in this diagram make up the fifth and sixth steps. The final de-hashing step occurs independently of Cell Ranger in a post-processing Jupyter notebook. 

# 10X Technician Spreadsheets
Below are 4 proposed spreadsheets for use by the 10X techs and not all experiment-related columns are shown. 

## 1. Sample-Level Spreadsheet
| Sample Name | Loading Sample | Expected Cell Number | Ref Trans | Chemistry | HTO | Library Features | Cell Ranger Verison |
|---|---|---|---|---|---|---|---|
| S1  | H1 | 3000 | GRCh38 | 3p | HTO-1 | LF1 | 3.1.0 |
| S2  | H1 | 4000 | GRCh38 | 3p | HTO-2 | LF1 | 3.1.0 |
| S3  | H1 | 5000 | GRCh38 | 3p | HTO-3 | LF1 | 3.1.0 |
| S4  | H1 | 6000 | GRCh38 | 3p | HTO-4 | LF1 | 3.1.0 |

### Columns
- `Sample Name`: the name of the biological sample being processed (see [Glossary])
- `Loading Sample`: the name of the sample being loaded into the 10x chip (see [Glossary]) that results in a set of partitioned single cells (e.g. GEM Group, see 10x glossary and [Glossary]). Usually, the `Loading Sample` is the same as the `Sample Name` - however this is not the case in hashing experiments.
- `Expected Cell Number`: the estimated number of cells in the loaded sample
- `Reference Transcriptome`: the reference transcriptome that reads are aligned to (very big files on AWS S3 buckets)
- `Chemistry`: the name of the 10x kit chemistry being used (e.g. 5-prime)
- `HTO`: the name of the hash tag oligo (HTO) that is used to label this sample, the value will be `-` for a non-hashed sample
- `Library Features`: this links a sample to its list of features in the [Library Features Table]. The value is `-` if we are not measuring any ADTs or HTOs

This spreadsheet shows four biological samples that are being hashed into a single loading sample (`H1`). Each sample is labeled with a different HTO (e.g. `HTO-1`) and share a common list of `Library Features` (e.g. all ADTs and HTOs used in the loading sample `H1`).

## 2. Library-Level Spreadsheet
| Library  | Loading Sample | 10x Lane | Library Type | Hashed Sample | Sample Index | Pooled Library | BCL | FASTQs |
|---|---|---|---|---|---|---|---|---|
| L1-GEX | H1 | XL1  | GEX  | True  | SI-GA-A3 | PL1 | BCL1 | FQ1-GEX |
| L1-ADT | H1 | XL1  | ADT  | True  |  RPI1    | PL1 | BCL1 | FQ1-ADT |
| L1-HTO | H1 | XL1  | HTO  | True  |  D7001   | PL1 | BCL1 | FQ1-HTO |

- `Library`: 
- `Loading Sample`: 
- `10x Lane`: lane number a sample is loaded into, necessary for keeping track of a single sample being loaded into multiple lanes
- `Library Type`: type of library being prepared (e.g. GEX, ADT)
  - **we haven't decided whether chemistry and version may or may not be included, e.g. GEX_5-prime**
  - as far as I know, we can use Total-Seq antibodies to combine ADT and HTO data into the same library (I think the convention is to call these libraries `-AH`)
 - `Hashed Sample`: whether a loaded sample has been hashed
 - `Sample Index`: the index that is used to label the sequencing library when pooling a library into a pooled library. 
   - 10x GEX libraries have index names like `S1-GA-A3` (4 different oligos)
   - ADT have `RPI` (single 6bp oligo)
   - HTO have `D700` (single 8bp oligo)
- `Pooled Library`: 
- `BCL`: name of the BCL file produced from sequencing the pooled library
-`FASTQs`: name of the Seq-Run FASTQ Set produced from a single sequencing run (e,g, `BCL1`) of the library

Libraries (or Sequencing Libraries) are the result of running a `Loading Sample` through a 10x chip lane. The 10x techs must keep track of library-level information during the course of a run, however from the perspective of the computational team, these libraries play more of an intermediate role. In our example, we have three libraries (`L1-GEX`, `L1-ADT`, `L1-HTO`) that are generated from a single 10x chip lane. These libraries will be indexed, pooled into a pooled-library (`PL1`), sequenced (resulting in `BCL1`), and ultimately result in three Seq-Run FASTQ sets (`FQ1-GEX`, `FQ1-ADT`, `FQ1-HTO`) - note that additional sequencing runs can produce additional sets). 

## 3. FASTQ-Level Spreadsheet
This is the Seq-Run-FASTQ Set level spreadsheet (see [Glossary]) that 10x techs will use to keep track of FASTQs produced from a sequencing run of a given pooled library. 

| FASTQs  | From BCL | To Output | Processing Run  | 
|---|---|---|---|
| FQ1-GEX | BCL1 | FBM1 | CR-1 |
| FQ1-ADT | BCL1 | FBM1 | CR-1 |
| FQ1-HTO | BCL1 | FBM1 | CR-1 |

### Columns
- `FASTQs`: name of the Seq-Run-FASTQ Set that is the result of a single sequencing run.
  - Name includes: `Loading Sample`, `10x Lane ID`, `BCL Run ID`, `Library Type` (our examples leave off redudant information in the FASTQ names)
  - Tracking the `BCL` name allows us to handle the common scenario where the same pooled librry (e.g. tube of liquid) is sequenced more than once (e.g. additional aliquots are taken from the tube and run on the sequencer).
- `From BCL`: name of the BCL file the FASTQs will be put into **or** some short-hand ID
- `To Output`: name of the output a FASTQ is contributing to (e.g. `FBM1`, `TCR1`)
- `Processing Run`: the name of the ["processing run"][`Processing-Run`] (see [Glossary]) that the data is being organized under (e.g. all jobs necessary to convert BCL(s) into FBM(s) and TCR/VDJ output(s)).

This spreadsheet shows three Seq-Run-FASTQ Sets that are obtained from processing the outputs from a single 10x chip lane (e.g. `XL-1`) to generate three sequencing libraries (`GEX`, `ADT`, and `HTO`), merging into a pooled library, sequencing, and then de-multiplexing the BCL file. Note, that the four biological samples from the [Sample-Level Spreadsheet] are not indicated in this table - this sample-level information will only be obtained after de-hashing after the Processing-Run.

## 4. Library Features Table
| Library Features | HIMC Feature Name |
|---|---|
| LF1 | HTO-1_H-101_3p_Lot# |
| LF1 | HTO-2_H-102_3p_Lot# |
| LF1 | HTO-3_H-103_3p_Lot# |
| LF1 | HTO-4_H-104_3p_Lot# |
| LF1 |   CD3_A-101_3p_Lot# |
| LF1 |   CD4_A-102_3p_Lot# |
| LF1 |   CD8_A-103_3p_Lot# |

### Columns
- `Library Features`: this is the name of the list of features used in a library and is referenced by the `Library Features` columns in the previous two spredsheets: [Sample-Level Spreadsheet] and [FASTQ-Level Spreadsheet].

- `HIMC Feature Name`: name of a feature (ADT or HTO) being measured
  - official gene symbol of the measured protein - ** might need to include species in name or lookup **
  - the unique HIMC oligo id (e.g. HIMC-1)
  - chemistry
  - the lot number (e.g. lot-1). 
- `Oligo ID`: the ID of the oligo sequence that was conjugated to the antibody (ADT or HTO).
- `Labeled Sample`: the sample that is being labeled by a feature - this is only used for HTOs and is redundant with the information in the [Sample-Level Spreadsheet]
 
This spreadsheet shows the list of `Library Features` that are associated with a loading sample (e.g. `H1`) and its subsequent sequencing libraries (`GEX`, `ADT`, `HTO`). This list is linked to specific samples and libraries in the two spreadsheets: [Sample-Level Spreadsheet] and [FASTQ-Level Spreadsheet].


## 5. Features Table
| HIMC Feature Name | Chemistry | Oligo ID | Oligo Sequence |  
|---|---|---|---|
| HTO-1_H-101_3p_Lot# | 3p | H-101 | ACTG |  
| HTO-2_H-102_3p_Lot# | 3p | H-102 | ACTG |  
| HTO-3_H-103_3p_Lot# | 3p | H-103 | ACTG |  
| HTO-4_H-104_3p_Lot# | 3p | H-104 | ACTG |  
|   CD3_A-101_3p_Lot# | 3p | A-101 | ACTG |  
|   CD4_A-102_3p_Lot# | 3p | A-102 | ACTG |  
|   CD5_A-103_3p_Lot# | 3p | A-103 | ACTG |  
| ... | ... | ... | ... |  

### Columns
- `HIMC Feature Name`: name of a feature (ADT or HTO) being measured
- `Chemistry`: the type of chemistry this feature is made for
- `Oligo`: the human readable name of the oligo used to label this feature
- `Sequence`: the actual oligo sequence 

This spreadsheet contains all features being used by the HIMC and each `HIMC Feature Name` is unique. 

# Processing-Run CSVs
A `Processing-Run` takes as input two spreadsheets (produced by the 10x techs using value-lookups) and one or more BCLs. The two spreadsheets are similar to the required spreadsheets that `cellranger mkfastq` and `count` take as inputs, but also contain additional information (e.g. expected cell count) as well as an implicit layout of running all jobs required to complete a  `Processing-Run` set of jobs.

## 1. HIMC Sample Sheet

| FASTQs | From BCL | To Output | Seq-Lanes | Index Name | Index Oligo | Library Type | Ref Trans | Number of Cells | Chemistry | Cell Ranger Version | Library Features |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **FQ1-GEX** | **BCL1** | **FBM1** | 1 | SI-GA-A3 | `-` | Gene Expression | GRCh38 | 18000 | 5p-V2 | 3.1.0 | LF1 |
| **FQ1-ADT** | **BCL1** | **FBM1** | 1 | RPI1 | ACTGTT | Custom | GRCh38 | 18000 | 5p-V2 | 3.1.0 | LF1 |
| **FQ1-HTO** | **BCL1** | **FBM1** | 1 | D7001 | ACTGTTGG | Custom | GRCh38 | 18000 | 5p-V2 | 3.1.0 | LF1 |

### Columns

- `FASTQs`: the **name of the Seq-Run-FASTQ set** obtained from the [FASTQ-Level Spreadsheet] which includes:
  - the **biological sample name** (needed to track which sample FBM should be generated from which FASTQs)
  - the **BCL file name** (needed to relate Seq-Run-FASTQ sets to specific BCL files)
- `From BCL`: name of the BCL file the FASTQs will be put into **or** some short-hand ID
- `To Output`: name of the output a FASTQ is contributing to (e.g. `FBM1`, `TCR1`)
- `Seq-Lanes`: the sequencing lanes used    
- `Index Name`: the name of the `Sample Index` obtained from the [FASTQ-Level Spreadsheet]
- `Index Oligo`: the actual index oligo sequence obtained from a Sample Index Spreadsheet (**not documented yet**). The value will be `-` for GEX index oligos since Cell Ranger mkfastq knows the meaning the index names (e.g. `SI-GA-3`).
- `Library Type`: the library type using the terminology acceptable to Cell Ranger Count (see [docs](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/using/feature-bc-analysis))
- `Reference Transcriptome`: the reference transcriptome used for alignment
- `Number of Cells`: the number of expected cells
- `Chemistry`: the 10x kit chemistry version

This CSV is a modified version of the simple CSV sample sheet for `mkfastq`, which now includes additional information required to perform multiple jobs within a Processing Run (e.g. multiple `mkfastq` and `count` jobs). This CSV will be used to construct both [the sample sheets CSV input for multiple `mkfastq` runs][10X Sample Sheet CSV] and [the libraries CSVs for multiple `count` runs][10X Libraries CSV]. The `Reference Transcriptome` and `Number of Cells` columns will be used to construct additional arguments for `cellranger count`. Additionally, the `Index Name` value will be used for GEX libraries, while the `Index Oligo` value will be used for Custom libraries (ADT/HTO).

## 2. HIMC Feature Reference CSV 

| Library Features | id | name | read | pattern | sequence | feature_type | 
|---|---|---|---|---|---|---|
| LF1 | HTO-1_H-101_3p_Lot# | HTO-1 | R2  | seq-pattern  | AACAAGACCCTTGAG  | Custom  |  
| LF1 | HTO-2_H-101_3p_Lot# | HTO-2 | R2  | seq-pattern  | CCCTTGAGAACAAGA  | Custom  |  
| LF1 | HTO-3_H-101_3p_Lot# | HTO-3 | R2  | seq-pattern  | AACATTGAGACCCAG  | Custom  |  
| LF1 | HTO-4_H-101_3p_Lot# | HTO-4 | R2  | seq-pattern  | TGAAACAAGACCCTG  | Custom  |  
| LF1 |   CD3_A-101_3p_Lot# |   CD3 | R2  | seq-pattern  | AACAACTTGAGGACC  | Custom  |  
| LF1 |   CD4_A-102_3p_Lot# |   CD4 | R2  | seq-pattern  | GGACCAAACAACTTG  | Custom  |  
| LF1 |   CD8_A-103_3p_Lot# |   CD8 | R2  | seq-pattern  | GGACCACTTGAACAA  | Custom  |  

### Columns
- `Library Features`: name of the list of features used in a library
- `id`: the unique id for the feature (can't collide with gene name)
- `name`: the human readable feature name (e.g. gene name, or hashtag number HTO-1)
- `read`: specifies which sequencing read contains the sequence (e.g. R2)
- `pattern`: specifies how to extract seq from read
- `sequence`: the nucleotide barcode seq associated with this feature (e.g. antibody barcode or scRNA protospacer sequence)
- `feature_type`: the type (e.g. Custom) from the list of acceptable feature types: `Custom` (preferred),  `Antibody Capture`,  or `CRISPR Guide Capture` (see [docs](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/using/feature-bc-analysis))
- (omitted columns )`target_gene_id`, `target_gene_name`: are optional CRISPR-specific columns that are not shown in the example above.

This spreadsheet is only necessary for feature barcoding (or CITE-seq) runs. It contains information on all the features used in a sequencing library. The addition of the `Library Features` column enables us to encode multiple libraries with different feature lableing schemes into a single sequencing run. Similarly, this scheme allows us to combine GEX only libraries (not shown) with feature-barcoding (or CITE-seq) libraries. 

# Cell Ranger Required CSVs

## 1. Sample Sheet CSV
| Lane| Sample | Index |
|---|---|---|
| 1  | FQ1-GEX | SI-GA-A3 |
| 1  | FQ1-ADT | ACTGTT |
| 1  | FQ1-HTO | ACTGTTGG |

### Columns
- `Lane`: which lane(s) of the flowcell to process. Can be either a single lane, a range (e.g., 2-4) or '*' for all lanes in the flowcell.
- `Sample`: The name of the sample. This name will be the prefix to all the generated FASTQs, and will correspond to the --sample argument in all downstream 10x pipelines.
Sample names must conform to the Illumina bcl2fastq naming requirements. Only letters, numbers, underscores and hyphens area allowed; no other symbols, including dots (".") are allowed. (the BCL name will be appended automatically by `mkfastq`; TODO: verify this).
- `Index` The 10x sample index set that was used in library construction, e.g., SI-GA-A12.
  - When processing custom oligos (e.g. ADT/HTO), pass the actual oligo sequences here.
 
This table is in the format of the "simple samplesheet" consumed by `cellranger mkfastq` (see 10x docs).

## 2. Libraries CSV
|  FASTQs | Sample  |  Library Type |
|---|---|---|
| /path/to/fastqs/ | FQ1-GEX | Gene Expression |
| /path/to/fastqs/ | FQ1-ADT | Custom |
| /path/to/fastqs/ | FQ1-HTO | Custom |

### Columns
- `FASTQs`: path to demultiplexed FASTQ files (cannot have comma-delimiited paths; more than one path requres an additional row).
- `Sample` is the sample name assigned in the `mkfastq` simple samplesheet.
- `Library Type` from documentation "The FASTQ data will be interpreted using the rows from the feature reference file that have a ‘feature_type’ that matches this library_type. This field is case-sensitive, and must match a valid library type as described in the Library / Feature Types section. Must be Gene Expression for the gene expression libraries. Must be one of Custom, Antibody Capture, or CRISPR Guide Capture for Feature Barcoding libraries."

This table is used by Cell Ranger Count to know which `FBM-FASTQ Set` (which is composed of at least one `Seq-Run-FASTQ Sets` from different sequencing runs, see [Glossary]) to aggregate into a single FBM, which includes GEX, ADT, and HTO data.

## 3. Feature Reference CSV

This is the same as the [Feature Reference CSV] that is produced by the 10x techs, but without the column `Library Features`. 

# Output CSVs
A single processing run will produce (at least) two output CSVs: 1) `Processing Status` and 2) `FASTQ meta-data`

## 1. Processing-Run Status CSV

| Job  | Status  | Output Path  | Download Link  |   
|---|---|---|---|
| mkfastq_BCL1  | Finished  | s3/path/to/zipped/fastqs  | pre-signed-URL  | 
| count_S1  | Pending  | s3/path/to/fbm  | pre-signed-URL  | 

### Columns
- `Job`: the name of the job
  - for `mkfastq` the name will be `mkfastq` and the name of the bcl file
  - for `count` the name will be `count` and the sample name. Since we can combine FASTQ data from multiple sequencing runs into a single FBM for a single sample (e.g. the `FBM-FASTQ Set`) we will name this job based on the sample name.
  - **need to decide on VDJ convention**
- `Status`: the current status of the job 
  - can be: `Pending`, `In-Progress`, `Finished`, or `Failed` 
- `Output Path`: path on the S3 bucket to the outputs of the job
- `Download Link`: a pre-signed URL for downloading the data off S3 buckets

This spreadsheet shows the status of the jobs associated with a single Processing-Run. This spreadsheet serves three purposes: 

1) Provide the 10x techs and computational teams with a simple way of checking the status of a Processing Run
2) Provide the pipeline a way to access the state of the Processing Run. For instance, it is a common scenario to receive multiple BCLs from the same sample (e.g. multiple sequencing runs) and we will need to start processing (e.g. get the number of reads from the FASTQs) before we obtain all BCLs. We would like to be able to add additional BCLs to a Processing-Run bucket and tell the Processing-Run job to complete the necesssary jobs that are available to complete. 

## 2. Processing-Run FASTQ Meta-Data CSV

This spreadsheet as a modified copy of the [HIMC Sample Sheet] that is used as input to a Processing-Run. We can append FASTQ meta-data such as reads-per-cell. 

**need to document this**

## 3. Processing-Run Sample Meta-Data CSV
This will give meta-data on loading sample level data. For a hashed sample, we will have to wait until manual de-hashing (not documented here) is run to get the individual samples from the hashed loading sample - otherwise a loading sample is a single biological sample. 

<!-- Nick is currently here --> 

# Enumeration of Scenarios

## 1. Single Lane per Sample, Single Seq-Run
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

## 2. Single Lane per Sample, Multiple Seq-Runs 
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

## 3. Multiple Lanes per Sample, Single Seq-Run

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

## 4. Multiple Lanes per Sample, Multiple Seq-Runs
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

## 5. One Lane per Sample, TCR-seq, Single Seq-Run
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

## 6. Multiple Lanes per Sample, TCR-seq, BCR-seq, Multiple Seq-Run
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

## 7. One Lane per Sample, ADT, Single Seq-Run
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

## 8. One Lane per Sample, ADT, Multiple Seq-Run
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

Three ADT samples are run in three lanes producing three GEX and three ADT libraries. These libraries are pooled and sequenced twice. The BCL files are de-multiplexed into twelve Seq-Run FASTQ Sets and three FBM FASTQ Sets (each containing GEX and ADT FASTQs). Cell Ranger `count` (using feature barcoding) is run three times to produce three FBMs containing both GEX and ADT data. 

## 9. Hashed-ADT, One Lane per Sample, Single Seq-Run
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

## 10. Hashed-ADT, Multiple Lanes per Sample, ADT, Single Seq-Run
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

# Glossary

The relationships between components in 10x single cell assay can be complicated. As a first step, we define a common vocabulary for ourselves below. We have ordered entities based on their natural progression during the experiment and data-processing steps.  

* **BCL files**: contains sequencing information on a pooled library (e.g. set of multiplexed sequencing libraries)

* **biological samples**: a cell suspension extracted from a single biological source, see [10x-Glossary](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/glossary)

* **Cell Ranger outputs**: Feature barcode matrix (FBM) which can be the product of several sequencing runs and BCL files, TCR/BCR contigs

* **FASTQs**: the products of de-multiplexing BCL files

* **FBM-FASTQ Set**: a set of FASTQs that will be used to generate a single FBM (feature barcode matrix). If the same pooled library is sequenced multiple times (producing multiple BCL files) we will need to combine multiple Seq-Run-FASTQ sets (see above) into a single FBM.

* **GEM Group**: A set of partitioned cells (Gelbeads-in-Emulsion) from a single 10x Chromium™ Chip channel. One or more sequencing libraries can be derived from a GEM Group.

* **loading sample**: the sample loaded into a 10x lane, which is usually the biological sample but may be a hash of many biological samples

* **library features list**: A list of features used in a library. The list will have a name like `LF1` in this documentation and the list includes all relevant hashtag and antibody features. 

* **pooled library**: a combination of several indexed sequencing libraries (from several 10x chip lanes) for loading into a sequencer and obtaining a BCL file

* **Processing-Run**: a set of cellranger mkfastq and count runs that take as input: 1) one or more BCL files and 2) Processing-Run Input CSV files. The Processing-Run produces the following outputs: 1) FASTQs, 2) FBMs (feature barcode matrices) and if applicable TCR/BCR data, 3) [Processing-Run Status CSV] which lists out all jobs in the Processing-Run as well as where to find outputs 4) [Processing-Run Meta-Data CSV] relevant metadata (still being sorted out) for 10x techs.

* **Sample-Level Outputs**: FBMs and VDJ data that has been re-organized into sample level data. This usually consists of copying sample level data out of the Processing Run, but for hashing runs requires manual de-hashing (post-Cell Ranger step).

* **Seq-Run-FASTQ Set**: a set of FASTQs that have been de-multiplexed from a single BCL file that give data for a single indexed sequencing library (e.g. a single GEX or ADT library). This set consists of lane- and read-specific FASTQs. 

* **sequencing libraries**: the end product(s) from a 10x chip lane. A single 10x lane can produce a single (e.g. GEX) or multiple sequencing libraries (e.g. GEX and VDJ; or GEX, ADT, and HTO). These sequencing libraries will either be pooled into a single pooled library and sequenced or run on separate sequencing runs (e.g. as is the case for VDJ and GEX which require different sequencing conditions)


[Glossary]: #glossary
[10x Technician Spreadsheets]: #10x-technician-spreadsheets
[Processing-Run CSVs]: #processing-run-csvs
[Cell Ranger Required CSVs]: #cell-ranger-required-csvs
[Output CSVs]: #output-csvs
[Feature Reference CSV]: #feature-reference-csv
[Library Features Table]: #3-library-features-table
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
