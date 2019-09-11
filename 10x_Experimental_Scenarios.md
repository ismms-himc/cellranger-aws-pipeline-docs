# 10x Experimental Scenarios
This document discusses proposed changes to the various spreadsheets used by HIMC techs who are running the assay, the computational team performing pre-processing, and the Cell Ranger software (e.g. we should shift to the most general input spreadsheet as arguments). This document heavily references the [10x documentation](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/using/mkfastq), defines schemas for the various spreadsheets used by all parties, and contains several example spreadsheets that represent different common experimental scenarios.

# Glossary

The relationships between components in 10x single cell assay can be complicated. As a first step, we define a common vocabulary for ourselves below. We have ordered entities based on their natural progression during the experiment and data-processing steps.  

* **biological samples**: a cell suspension extracted from a single biological source, see [10x-Glossary](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/glossary)

* **loading sample**: the sample loaded into a 10x lane, which is usually the biological sample but may be a hash of many biological samples

* **sequencing libraries**: the end product(s) from a 10x chip lane. A single 10x lane can produce a single (e.g. GEX) or multiple sequencing libraries (e.g. GEX and VDJ; or GEX, ADT, and HTO). These sequencing libraries will either be pooled into a single pooled library and sequenced or run on separate sequencing runs (e.g. as is the case for VDJ and GEX which require different sequencing conditions)

* **pooled library**: a combination of several indexed sequencing libraries (from several 10x chip lanes) for loading into a sequencer and obtaining a BCL file

* **BCL files**: contains sequencing information on a pooled library (e.g. set of multiplexed sequencing libraries)

* **FASTQs**: the products of de-multiplexing BCL files

* **Seq-Run-FASTQ Set**: a set of FASTQs that have been de-multiplexed from a single BCL file that give data for a single indexed sequencing library (e.g. a single GEX or ADT library). This set consists of lane- and read-specific FASTQs. 

* **FBM-FASTQ Set**: a set of FASTQs that will be used to generate a single FBM (feature barcode matrix). If the same pooled library is sequenced multiple times (producing multiple BCL files) we will need to combine multiple Seq-Run-FASTQ sets (see above) into a single FBM.

* **Processing-Run**: a set of cellranger mkfastq and count runs that take as input: 1) one or more BCL files and 2) Processing-Run Input CSV files. The Processing-Run produces the following outputs: 1) FASTQs, 2) FBMs (feature barcode matrices) and if applicable TCR/BCR data, 3) [Processing-Run Status CSV] which lists out all jobs in the Processing-Run as well as where to find outputs 4) [Processing-Run Meta-Data CSV] relevant metadata (still being sorted out) for 10x techs.

* **Cell Ranger outputs**: Feature barcode matrix (FBM) which can be the product of several sequencing runs and BCL files, TCR/BCR contigs

* **Sample-Level Outputs**: FBMs and VDJ data that has been re-organized into sample level data. This usually consists of copying sample level data out of the Processing Run, but for hashing runs requires manual de-hashing (post-Cell Ranger step).

# 10x Examples from Documentation
Below are two experimental scenarios from 10x that have been paraphrased into our vocabulary (see [Glossary]). 

### 2 Samples, 2 Seq-Libraries, 1 Seq-Run, 2 FBMs
[![Schematic of 2-sample, 1-seq-run workflow](https://support.10xgenomics.com/img/mkfastq-1.png "")](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/using/mkfastq#example_workflows)

> In this example, we have two 10x libraries (each processed through a separate Chromium chip channel) that are multiplexed on a single flowcell. Note that after running `cellranger mkfastq`, we run a separate instance of the pipeline on each library

### 1 Sample, 1 Seq-Library, 2 Seq-Run, 1 FBM
[![Schematic of 1-sample, 2-seq-run workflow](https://support.10xgenomics.com/img/mkfastq-2.png "")](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/using/mkfastq#example_workflows)

> In this example, we have one 10x library sequenced on two flowcells. Note that after running cellranger mkfastq, we run a single instance of the pipeline on all the FASTQ files generated.

The common scenario of sequencing the same 'sequencing library' more than once (in the above example) is the reason why the 10x technicians are moving towards a FASTQ-level organization (rather than a 'sequencing library' a.k.a. 'pooled library' level).

# 10X Technician Spreadsheets
Below are 4 proposed spreadsheets for use by the 10X techs (not all experiment-related columns are shown). The spreadsheets produced in these three sections ([10x Technician Spreadsheets], [Processing-Run CSVs], and [Cell Ranger Required CSVs]) are all based on the same example: Four biological samples that are hashed together, measure three surface markers (3 ADTs), and are run on a single 10x chip lane. 

## 1. Sample-Level Spreadsheet
| Sample Name | Loading Sample | Expected Cell Number | Reference Transcriptome | Chemistry | HTO | Library Features |
|---|---|---|---|---|---|---|
| S1  | H1 | 3000 | GRCh38 | 3p | HTO-1 | LF-1 |
| S2  | H1 | 4000 | GRCh38 | 3p | HTO-2 | LF-1 |
| S3  | H1 | 5000 | GRCh38 | 3p | HTO-3 | LF-1 |
| S4  | H1 | 6000 | GRCh38 | 3p | HTO-4 | LF-1 |

### Columns
- `Sample Name`: the name of the biological sample being processed (see [Glossary])
- `Loading Sample`: the name of the sample being loaded into the 10x chip (see [Glossary])
- `Expected Cell Number`: the estimated number of cells in the loaded sample
- `Reference Transcriptome`: the reference transcriptome that reads are aligned to (very big files on AWS S3 buckets)
- `Chemistry`: the name of the 10x kit chemistry being used (e.g. 5-prime)
- `HTO`: the name of the hash tag oligo (HTO) that is used to label this sample, the value will be `-` for a non-hashed sample
- `Library Features`: this links a sample to its list of features in the [Library Features Table]. The value is `-` if we are not measuring any ADTs or HTOs

### Explanation of this spreadsheet
This spreadsheet shows four biological samples that are being hashed into a single loading sample (`H1_GEX`). Each sample is labeled with a different HTO (e.g. `HTO-1`) and share a common list of `Library Features` (e.g. all ADTs and HTOs used in the hashed `Loading Sample` `H1_GEX`).

## 2. FASTQ-Level Spreadsheet
This is the Seq-Run-FASTQ Set level spreadsheet (see [Glossary]) that 10x techs will use to keep track of FASTQs produced from a sequencing run of a given pooled library. 

| FASTQs  | Loading Sample | Sample Index | Hashed Sample | 10x Lane ID | Library Type | BCL Run ID  | Processing Run  | Library Features |
|---|---|---|---|---|---|---|---|---|
| H1_XL-1_BCL-1_GEX | H1 | SI-GA-A3 | True  | XL-1  | GEX  | BCL-1 | CR-1 | LF-1 |
| H1_XL-1_BCL-1_ADT | H1 | RPI-1    | True  | XL-1  | ADT  | BCL-1 | CR-1 | LF-1 | 
| H1_XL-1_BCL-1_HTO | H1 | D700-1   | True  | XL-1  | HTO  | BCL-1 | CR-1 | LF-1 |

### Columns
- `FASTQs`: name of the Seq-Run-FASTQ Set that is the result of a single sequencing run.
  - Composed of the `Loading Sample` name, the `10x Lane ID`, the `BCL Run ID`, and `Library Type`
  - Tracking the `BCL Run ID` allows us to handle the common scenario where the same sequencing pool (e.g. tube of liquid) is sequenced more than once (more than one aliquot is taken from the tube and run on the sequencer).
- `Loading Sample`: name of the sample that is loaded into a 10x chip lane (can consist of several biolofical samples via hashing).
- `Sample Index`: the index that is used to label the sequencing library when pooling the library into a pooled library. 10x GEX libraries have index names like `S1-GA-A3` (4 different oligos); ADT have `RPI` (single 6bp oligo), and HTO have `D700` (single 8bp oligo)
- `Hashed Sample`: True/False, indicates whether hashing has been done (will be redundant with the `Loading Sample` naming convention).
- `10x Lane ID`: lane number a sample is loaded into
  - necessary for situations where the same sample is loaded into several lanes (to measure more cells from a sample)
  - becomes part of the FASTQs' names
- `Library Type`: type of library being prepared (e.g. GEX, ADT)
  - **we haven't decided whether chemistry and version may or may not be included, e.g. GEX_5-prime**
  - as far as I know, we can use Total-Seq antibodies to combine ADT and HTO data into the same library (I think the convention is to call these libraries `-AH`)
- `BCL Run ID`: name of the BCL file the FASTQs will be put into **or** some short-hand ID
- `Processing Run`: the name of the ["processing run"][`Processing-Run`] (see [Glossary]) that the data is being organized under (e.g. all jobs necessary to convert BCL(s) into FBM(s) and TCR/VDJ output(s)).
- `Library Features`: this links a sample to its list of features in the [Library Features Table]. The value is `-` if we are not measuring any ADTs or HTOs

### Explanation of this spreadsheet
This spreadsheet shows three Seq-Run-FASTQ Sets that are obtained from processing the outputs from a single 10x chip lane (e.g. `XL-1`) to generate three sequencing libraries (`GEX`, `ADT`, and `HTO`), merging into a pooled library, sequencing, and then de-multiplexing the BCL file. Note, that the four biological samples from the [Sample-Level Spreadsheet] are not indicated in this table - this sample-level information will only be obtained after de-hashing after the Processing-Run.

## 3. Library Features Table
| Library Features | HIMC Feature Name | Oligo ID | Labeled Sample |
|---|---|---|---|
| LF-1 | HTO-1_H-101_3p_Lot-# | H-101 | S1 |
| LF-1 | HTO-2_H-102_3p_Lot-# | H-102 | S2 |
| LF-1 | HTO-3_H-103_3p_Lot-# | H-103 | S3 |
| LF-1 | HTO-4_H-104_3p_Lot-# | H-104 | S4 |
| LF-1 |   CD3_A-101_3p_Lot-# | A-101 | - |
| LF-1 |   CD4_A-102_3p_Lot-# | A-102 | - |
| LF-1 |   CD8_A-103_3p_Lot-# | A-103 | - |

### Columns
- `Library Features`: this is the name of the list of features used in a library and is referenced by the `Library Features` columns in the previous two spredsheets: [Sample-Level Spreadsheet] and [FASTQ-Level Spreadsheet].

- `HIMC Feature Name`: name of a feature (ADT or HTO) being measured
  - official gene symbol of the measured protein 
  - the unique HIMC oligo id (e.g. HIMC-1)
  - chemistry
  - the lot number (e.g. lot-1). 
- `Oligo ID`: the ID of the oligo sequence that was conjugated to the antibody (ADT or HTO).
- `Labeled Sample`: the sample that is being labeled by a feature - this is only used for HTOs and is redundant with the information in the [Sample-Level Spreadsheet]
 
### Explanation of this spreadsheet
This spreadsheet shows the list of `Library Features` that are associated with a loading sample (e.g. `H1`) and its subsequent sequencing libraries (`GEX`, `ADT`, `HTO`). This list is linked to specific samples and libraries in the two spreadsheets: [Sample-Level Spreadsheet] and [FASTQ-Level Spreadsheet].


## 4. Features Table
| HIMC Feature Name | Chemistry | Oligo ID | Oligo Sequence |  
|---|---|---|---|
| HTO-1_H-101_3p_Lot-# | 3p | H-101 | ACTG |  
| HTO-2_H-102_3p_Lot-# | 3p | H-102 | ACTG |  
| HTO-3_H-103_3p_Lot-# | 3p | H-103 | ACTG |  
| HTO-4_H-104_3p_Lot-# | 3p | H-104 | ACTG |  
|   CD3_A-101_3p_Lot-# | 3p | A-101 | ACTG |  
|   CD4_A-102_3p_Lot-# | 3p | A-102 | ACTG |  
|   CD5_A-103_3p_Lot-# | 3p | A-103 | ACTG |  
| ... | ... | ... | ... |  

### Columns
- `HIMC Feature Name`: name of a feature (ADT or HTO) being measured
- `Chemistry`: the type of chemistry this feature is made for
- `Oligo`: the human readable name of the oligo used to label this feature
- `Sequence`: the actual oligo sequence 

### Explanation of this spreadsheet
This spreadsheet contains all features being used by the HIMC and each `HIMC Feature Name` is unique. 

# Processing-Run CSVs
A `Processing-Run` takes as input two spreadsheets (produced by the 10x techs using value-lookups) and one or more BCLs. The two spreadsheets are similar to the required spreadsheets that `cellranger mkfastq` and `count` take as inputs, but also contain additional information (e.g. expected cell count) as well as an implicit layout of running all jobs required to complete a  `Processing-Run` set of jobs.

## 1. Custom Sheet CSV

| Lane| Sample | Index Name | Index Oligo | Library Type | Reference Transcriptome | Number of Cells | Chemistry |
|---|---|---|---|---|---|---|---|
| 1  | H1_XL-1_BCL-1_GEX | SI-GA-A3 | `-` | Gene Expression | GRCh38 | 18000 | 5-prime_V2 |
| 2  | H1_XL-1_BCL-1_ADT | RPI-1 | ACTGTT | Custom | GRCh38 | 18000 | 5-prime_V2 |
| 3  | H1_XL-1_BCL-1_HTO | D700-1 | ACTGTTGG | Custom | GRCh38 | 18000 | 5-prime_V2 |

### Columns
- `Lane`: the 10x chip lane **I think we can just increment this**
- `Sample`: the name of the Seq-Run-FASTQ set **(I think)** obtained from the [FASTQ-Level Spreadsheet]
- `Index Name`: the name of the `Sample Index` obtained from the [FASTQ-Level Spreadsheet]
- `Index Oligo`: the actual index oligo sequence obtained from a Sample Index Spreadsheet (**not documented yet**). The value will be `-` for GEX index oligos since Cell Ranger mkfastq knows the meaning the index names (e.g. `SI-GA-3`).
- `Library Type`: the library type using the terminology acceptable to Cell Ranger Count (see [docs](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/using/feature-bc-analysis))
- `Reference Transcriptome`: the reference transcriptome used for alignment
- `Number of Cells`: the number of expected cells
- `Chemistry`: the 10x kit chemistry version

### Explanation of this spreadsheet

This CSV will be used to construct both [the sample sheet CSV input for `mkfastq`][10X Sample Sheet CSV] and [the libraries CSV for `count`][10X Libraries CSV]. The `Reference Transcriptome` and `Number of Cells` columns will be used to construct additional arguments for `cellranger count`. Additionally, the `Index Name` value will be used for GEX libraries, while the `Index Oligo` value will be used for Custom libraries (ADT/HTO).

## 2. Feature Reference CSV 

| id | name | read | pattern | sequence | feature_type | 
|---|---|---|---|---|---|
| HTO-1_H-101_3p_Lot-# | HTO-1 | R2  | 5PNNNNNNNNNN(BC)NNNNNNNNN  | AACAAGACCCTTGAG  | Custom  |  
| HTO-2_H-101_3p_Lot-# | HTO-2 | R2  | 5PNNNNNNNNNN(BC)NNNNNNNNN  | CCCTTGAGAACAAGA  | Custom  |  
| HTO-3_H-101_3p_Lot-# | HTO-3 | R2  | 5PNNNNNNNNNN(BC)NNNNNNNNN  | AACATTGAGACCCAG  | Custom  |  
| HTO-4_H-101_3p_Lot-# | HTO-4 | R2  | 5PNNNNNNNNNN(BC)NNNNNNNNN  | TGAAACAAGACCCTG  | Custom  |  
|   CD3_A-101_3p_Lot-# |   CD3 | R2  | 5PNNNNNNNNNN(BC)NNNNNNNNN  | AACAACTTGAGGACC  | Custom  |  
|   CD4_A-102_3p_Lot-# |   CD4 | R2  | 5PNNNNNNNNNN(BC)NNNNNNNNN  | GGACCAAACAACTTG  | Custom  |  
|   CD8_A-103_3p_Lot-# |   CD8 | R2  | 5PNNNNNNNNNN(BC)NNNNNNNNN  | GGACCACTTGAACAA  | Custom  |  

### Columns
- `id`: the unique id for the feature (can't collide with gene name)
- `name`: the human readable feature name (e.g. gene name, or hashtag number HTO-1)
- `read`: specifies which sequencing read contains the sequence (e.g. R2)
- `pattern`: specifies how to extract seq from read
- `sequence`: the nucleotide barcode seq associated with this feature (e.g. antibody barcode or scRNA protospacer sequence)
- `feature_type`: the type (e.g. Custom) from the list of acceptable feature types: `Custom` (preferred),  `Antibody Capture`,  or `CRISPR Guide Capture` (see [docs](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/using/feature-bc-analysis))
- (omitted columns )`target_gene_id`, `target_gene_name`: are optional CRISPR-specific columns that are not shown in the example above.

### Explanation of this Spreadsheet
This spreadsheet is only necessary for feature barcoding (or CITE-seq) runs. It contains information on all the features used in a sequencing library. **I'm not sure how we will handle cases where different feature labeling schemes are pooled into a single sequencing pool (or if this ever happens).**

# Cell Ranger Required CSVs

## 1. Sample Sheet CSV
| Lane| Sample | Index |
|---|---|---|
| 1  | H1_XL-1_BCL-1_GEX | SI-GA-A3 |
| 1  | H1_XL-1_BCL-1_ADT | ACTGTT |
| 1  | H1_XL-1_BCL-1_HTO | ACTGTTGG |

### Columns
- `Lane` refers to the 10x chip lane.
- `Sample` refers to our loading sample name (the BCL name will be appended automatically by `mkfastq`; TODO: verify this).
- `Index` refers to the oligos used to de-multiplex the BCL
  - When processing custom oligos (e.g. ADT/HTO), pass the actual oligo sequences here.
 
### Explanation of this spreadsheet
This table is in the format of the "simple samplesheet" consumed by `cellranger mkfastq` (see 10x docs).

## 2. Libraries CSV
|  FASTQs | Sample  |  Library Type |
|---|---|---|
| /path/to/fastqs/ | H1_XL-1_BCL-1_GEX | Gene Expression |
| /path/to/fastqs/ | H1_XL-1_BCL-1_ADT | Custom |
| /path/to/fastqs/ | H1_XL-1_BCL-1_HTO | Custom |

### Columns
- `FASTQs`: path to demultiplexed FASTQ files (cannot have comma-delimiited paths; more than one path requres an additional row).
- `Sample` is the sample name assigned in the `mkfastq` simple samplesheet.
- `Library Type` from documentation "The FASTQ data will be interpreted using the rows from the feature reference file that have a ‘feature_type’ that matches this library_type. This field is case-sensitive, and must match a valid library type as described in the Library / Feature Types section. Must be Gene Expression for the gene expression libraries. Must be one of Custom, Antibody Capture, or CRISPR Guide Capture for Feature Barcoding libraries."

### Explanation of this table 
This table is used by Cell Ranger Count to know which `FBM-FASTQ Set` (which is composed of at least one `Seq-Run-FASTQ Sets` from different sequencing runs, see [Glossary]) to aggregate into a single FBM, which includes GEX, ADT, and HTO data.

## 3. Feature Reference CSV

This is the same as the [Feature Reference CSV] that is produced by the 10x techs.

# Output CSVs
A single processing run will produce (at least) two output CSVs: 1) `Processing Status` and 2) `FASTQ meta-data`

## Processing-Run Status CSV


## Processing-Run Meta-Data CSV

# Enumeration of Scenarios

<!-- which tables' schemas are being represented in these examples? --> 

## scRNA-seq: 3 Samples, 3 10x Lanes, 3 Seq-Libraries, 1 Flowcell/BCL
These three rows represents an experiment (e.g. Cell Ranger Run `CR-1`) that has three samples (`S1`, `S2`, `S3`) run in separate 10x chip lanes. The three libraries generated from the three lanes are multiplexed and run in a single flowcell, which generates a single BCL file (`BCL-1`). This single BCL file will need to be de-multiplexed, producing three sets of FASTQs that will produce three 
feature-barcode-matrices (FBMs). 

| Library  | Sample  | BCL  | Cell Ranger Run  |   
|---|---|---|---|
| S1_GEX  | S1  | BCL-1  | CR-1  |   
| S2_GEX  | S2  | BCL-1  | CR-1  |   
| S3_GEX  | S3  | BCL-1  | CR-1  |  

```
BCL-1 -> FASTQs-1 -> FBM-1
      -> FASTQs-2 -> FBM-2
      -> FASTQs-3 -> FBM-3
```
### CITE-seq and Hashtagging: 2 Samples, 1 10x Lane, 3 Seq-Libraries (GEX, ADT, HTO), 1 Flowcell/BCL
The second set of three rows represents a CITE-seq and hashtag experiment (`CR-2`) that has two samples (`S4`, `S5`) run in one 10x chip lane, which produces three libraries (`S4_GEX`, `S4_ADT`, `S4_HTO`)

| Library  | Sample  | BCL  | Processing Run  |  Hashed |
|---|---|---|---|---|
| S_GEX  | S4_S5  | BCL-2  | CR-2  |   |
| S_ADT  | S4_S5  | BCL-2  | CR-2  |   |
| S_HTO  | S4_S5  | BCL-2  | CR-2  |    |

```   
mkfastq              count     de-hashtag
BCL-2 -> FASTQs_GEX -> FBM -> FBM_S4
      -> FASTQs_ADT           FBM_S5
      -> FASTQs_HTO    
```

## scRNA-seq (pooled run): One Sample, Three Seq-Libraries, Three Flowcell/BCLs

| Library  | Sample  | BCL  | Cell Ranger Run  |   
|---|---|---|---| 
| S6_GEX_A  | S6  | BCL-3  | CR-3  |
| S6_GEX_B  | S6  | BCL-4  | CR-3  |   
| S6_GEX_C  | S6  | BCL-5  | CR-3  |  



[Glossary]: #glossary
[10x Technician Spreadsheets]: #10x-technician-spreadsheets
[Processing-Run CSVs]: #processing-run-csvs
[Cell Ranger Required CSVs]: #cell-ranger-required-csvs
[Feature Reference CSV]: #feature-reference-csv
[Library Features Table]: #3-library-features-table
[`Processing-Run`]: #processing-run-spreadsheets
[10X Sample Sheet CSV]: #1-sample-sheet-csv
[10X Libraries CSV]: #2-libraries-csv
[Processing-Run Status CSV]: #processing-run-status-csv
[Processing-Run Meta-Data CSV]: #processing-run-meta-data-csv
[Sample-Level Spreadsheet]: #1-sample-Level-spreadsheet
[FASTQ-Level Spreadsheet]: #2-fastq-Level-spreadsheet
[Features Table]: #4-features-table
