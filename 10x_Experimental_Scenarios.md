# 10x Experimental Scenarios
This document discusses proposed changes to the various spreadsheets used by HIMC techs who are running the assay, the computational team performing pre-processing, and the Cell Ranger software (e.g. we should shift to the most general input spreadsheet as arguments). This document heavily references the [10x documentation](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/using/mkfastq), defines schemas for the various spreadsheets used by all parties, and contains several example spreadsheets that represent different common experimental scenarios.

# Glossary

The relationships between components in 10x single cell assay can be complicated. As a first step, we define a common vocabulary for ourselves below. We have ordered entities based on their natural progression during the experiment and data-processing steps.  

* **biological samples**: a cell suspension extracted from a single biological source, see [10x-Glossary](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/glossary)

* **loading sample**: the sample loaded into a 10x lane, which is usually the biological sample but may be a hash of many biological samples

* **sequencing libraries**: the end product from a 10x chip lane

* **pooled sample**: a combination of several indexed sequencing libraries (from several 10x chip lanes) for loading into a sequencer and obtaining a BCL file

* **BCL files**: contains sequencing information on a pooled sample (e.g. set of multiplexed sequencing libraries)

* **FASTQs**: the product of de-multiplexing BCL files, sub-divided by lane and read

* **Processing-Run**: a set of cellranger mkfastq and count runs that take as input: 1) one or more BCL files and 2) Processing-Run Input CSV files. The Processing-Run produces the following outputs: 1) FASTQs, 2) FBMs (feature barcode matrices) and if applicable TCR/BCR data, 3) [Processing-Run Status CSV] which lists out all jobs in the Processing-Run as well as where to find outputs 4) Processing-Run Meta-Data CSV relevant metadata (still being sorted out) for 10x techs.

* **Cell Ranger outputs**: Feature barcode matrix (FBM) which can be the product of several sequencing runs and BCL files, TCR/BCR contigs

* **Sample-Level Outputs**: FBMs and VDJ data that has been re-organized into sample level data. This usually consists of copying sample level data out of the Processing Run, but for hashing runs requires manual de-hashing (post-Cell Ranger step).

# 10x Examples from Documentation
Below are two experimental scenarios from 10x that have been paraphrased into our vocabulary (see [Glossary]). 

### 2 Samples, 2 Seq-Libraries, 1 Seq-Run/Flowcell, 2 FBMs
[![Schematic of 2-sample, 1-seq-run workflow](https://support.10xgenomics.com/img/mkfastq-1.png "")](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/using/mkfastq#example_workflows)

> In this example, we have two 10x libraries (each processed through a separate Chromium chip channel) that are multiplexed on a single flowcell. Note that after running `cellranger mkfastq`, we run a separate instance of the pipeline on each library

### 1 Sample, 1 Seq-Library, 2 Seq-Run/Flowcells, 1 FBM
[![Schematic of 1-sample, 2-seq-run workflow](https://support.10xgenomics.com/img/mkfastq-2.png "")](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/using/mkfastq#example_workflows)
> In this example, we have one 10x library sequenced on two flowcells. Note that after running cellranger mkfastq, we run a single instance of the pipeline on all the FASTQ files generated.

The common scenario of sequencing the same 'sequencing library' more than once (in the above example) is the reason why the 10x technicians are moving towards a FASTQ-level organization (rather than a 'sequencing library' a.k.a. 'pooled library' level).

# Proposed 10X Technician Spreadsheets
Below are 4 proposed spreadsheets for use by the 10X techs (not all experiment-related columns are shown).

## 1. Sample-Level Spreadsheet
| Sample Name  | Loading Sample |  Sample Metadata ... | HTO | Expected Cell Number | Library Features |
|---|---|---|---|---|---|
| S1_GEX  | H1_GEX | ... | HTO-1  | 5000 | LF-1 |

<!-- Difference b/t Sample name and Loading sample? -->
A CITE-seq sequencing-library will, in general, contain ADTs and HTOs. <!-- Should there be an ADTs column? -->
- `Sample Metadata`: will include necessary Cell Ranger information like organism, reference transcriptome, etc.
- `Library`: link to the [Library Features Table] below.
<!-- other column descriptions? -->

## 2. FASTQ-Level Spreadsheet
Laura is working on making a new "FASTQ-oriented" spreadsheet, but that nomenclature is tricky: we're not considering individual run- and read-level FASTQs, but are referring to such a group collectively as a "FASTQ" or "set of FASTQs".

Below is the in-progress outline for this spreadsheet, along with some example configurations:

| FASTQs  | Loading Sample | Hashed Sample | 10x Lane ID | Library Type | BCL Run ID  | Processing Run  |   
|---|---|---|---|---|---|---|
| H1_GEX_BCL-1 | H1_GEX  | False  | 1  | GEX  | BCL-1 | CR-1 |

- `FASTQs`: name of the "set of FASTQs" that will be fed to a single `cellranger count` run.
  - Composed of the `Loading Sample` name appended with the `BCL Run ID`.
  - Allows us to handle the common scenario where the same sequencing library (e.g. tube of liquid that can be aliquoted from) is sequenced more than once.
- `Loading Sample`: name of the sample that is loaded into a 10x chip lane (can consist of several samples via hashing).
- `Hashed Sample`: True/False, indicates whether hashing has been done (will be redundant with the `Loading Sample` naming convention).
- `10x Lane ID`: lane number a sample is loaded into
  - necessary for situations where the same sample is loaded into several lanes
  - (becomes part of the FASTQs' names in that case)
- `Library Type`: type of library being prepared (e.g. GEX, ADT)
  - Chemistry and version may or may not be included, e.g. GEX_5-prime.
- `BCL Run ID`: name of the BCL file the FASTQs will be put into.
- `Processing Run`: name of the ["processing run"][`Processing-Run`] that the data is being organized under (a processing run consists of the jobs necessary to convert BCL inputs into FBM and TCR/VDJ outputs).


## 3. Library Features Table
| Library | Feature | Index |
|---|---|---|
| LF-1 | HTO-1   | HTO-Index-1 |
| LF-1 | HTO-2   | HTO-Index-2 |
| LF-1 | HTO-3   | HTO-Index-3 |
| LF-1 | CD8_HIMC-1_Lot-1  | ADT-Index-1 |
| … | …  | … |
| LF-2 | CD3_HIMC-1_Lot-1  | ADT-Index-2 |
| LF-2 | CD4_HIMC-1_Lot-1  | ADT-Index-3 |

Each library has a set of feature/index pairs associated with it, and these mappings are stored in the Library Features Table.

The `Feature` names contain the following underscore-delimited components:
1) official gene symbol of the measured protein (or the protein instead if desired - otherwise other names will be stored as aliases)
2) the unique HIMC id (e.g. HIMC-1), and the lot number (e.g. lot-1).

The `Index` column contains the oligo index IDs that can be looked up in [the `Features Table`][Library Features Table].

## 4. Features Table
| HIMC Feature Name | Chemistry | Index Name | Sequence |  
|---|---|---|---|
| CD8_HIMC-1_Lot-1 | 5-prime | ADT-Index-1 | ACTG |  

# Processing-Run Spreadsheets
A `Processing-Run` takes as input two spreadsheets (produced by the 10x techs) and one or more BCLs. The two spreadsheets are similar to the required spreadsheets that `cellranger mkfastq` and `count` take as inputs, but also contain additional information (e.g. expected cell count) as well as an implicit layout of running all jobs required to complete a  `Processing-Run` set of jobs.

## 1. Custom Sheet CSV

| Lane| Sample | Index | Library Type | Reference Transcriptome | Number of Cells | Chemistry |
|---|---|---|---|---|---|---|
| 1  | S1_GEX | SI-GA-A3 | Gene Expression | GRCh38 | 3000 | 5-prime_V2 |

This CSV will be used to construct [the sample sheet CSV input for `mkfastq`][10X Sample Sheet CSV] as well as [the libraries CSV for `count`][10X Libraries CSV]. The last two columns will be used to construct additional arguments for `cellranger count`.

## 2. Feature Reference CSV 

| id | name | read | pattern | sequence | feature_type | 
|---|---|---|---|---|---|
| CD3  | CD3_TotalSeqB  | R2  | 5PNNNNNNNNNN(BC)NNNNNNNNN  | AACAAGACCCTTGAG  | Antibody Capture  |  


This document is only necessary for feature barcode (FBM) runs:
- `id`: unique id for the feature (can't collide with gene name)
- `name`: human readable feature name (e.g. gene name)
- `read`: specifies which sequencing read contains the sequence (e.g. R2)
- `pattern`: specifies how to extract seq from read
- `sequence`: Nucleotide barcode seq associated with this feature (e.g. antibody barcode or scRNA protospacer sequence)
- `feature_type`: (e.g. custom <!-- more info? -->)
- `target_gene_id`, `target_gene_name`: are optional CRISPR-specific columns that are not shown in the example above.


The 10x techs will produce the feature reference CSV (presumably via lookup tables). <!-- more info? -->


# Cell Ranger Required CSVs

## Sample Sheet CSV
| Lane| Sample | Index |
|---|---|---|
| 1  | S1_GEX | SI-GA-A3 |

This table is in the format of the "simple samplesheet" consumed by `cellranger mkfastq`:
- `Lane` refers to the 10x chip lane.
- `Sample` refers to our loading sample name (the BCL name will be appended automatically by `mkfastq`; TODO: verify this).
- `Index` refers to the oligos used to de-multiplex the BCL
  - When processing custom oligos (e.g. ADT/HTO), pass the actual oligo sequences here.

## Libraries CSV
|  FASTQs | Sample  |  Library Type |
|---|---|---|
| /path/to/fastqs/ | S1_GEX_BCL-1 | Gene Expression |
| /path/to/fastqs/ | S1_HTO_BCL-1 | Custom |

- `FASTQs`: path to demultiplexed FASTQ files (cannot have comma-delimiited paths; more than one path requres an additional row).
- `Sample` is the sample name assigned in the `mkfastq` simple samplesheet.
- `Library Type` should be self-explanatory. <!-- Can we enumerate the possibilities here? Are they referenced anywhere else, or is this just a free-form "Notes" type of field? -->

## Feature Reference CSV

This is the same as the [Feature Reference CSV]

# Output CSVs
A single processing run will produce two output CSVs: 1) `Processing Status` and 2) `FASTQ meta-data`

## Processing-Run Status CSV


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


[Processing-Run Status CSV]: #processing-run-status-csv
[Glossary]: #glossary
[Feature Reference CSV]: #feature-reference-csv
[Library Features Table]: #library-features-table
[`Processing-Run`]: #processing-run-spreadsheets
[10X Sample Sheet CSV]: #sample-sheet-csv
[10X Libraries CSV]: #libraries-csv
