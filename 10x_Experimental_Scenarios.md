# 10x Experimental Scenarios
This document discusses proposed changes to the organization of sequencing run spreadsheets used by HIMC technicians running the 10x assay and the computational team performing pre-processing. This document heavily references the [10x documentation](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/using/mkfastq).

# Background
The relationship between **biological samples** (e.g. a cell suspension extracted from a single biological source, see [glossary](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/glossary)), **sequencing libraries** (e.g. the end product from a 10x chip lane), **BCL files** (e.g. generally multiplexed from several sequencing libraries), **FASTQs** (e.g. the product of de-multiplexing BCL files, sub-divided by lane and read), **Cell Ranger pre-processing runs** (e.g. can utilize several BCL files for a pooled run), and **Cell Ranger outputs** (e.g. Feature barcode matrix (FBM), TCR/BCR contigs) can be complicated. Two examples from the documentation are shown below.

### 2 Samples, 2 Seq-Libraries, 1 Seq-Run/Flowcell, 2 FBMs
[![Schematic of 2-sample, 1-seq-run workflow](https://support.10xgenomics.com/img/mkfastq-1.png "")](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/using/mkfastq#example_workflows)

> In this example, we have two 10x libraries (each processed through a separate Chromium chip channel) that are multiplexed on a single flowcell. Note that after running `cellranger mkfastq`, we run a separate instance of the pipeline on each library

### 1 Sample, 1 Seq-Library, 2 Seq-Run/Flowcells, 1 FBM
[![Schematic of 1-sample, 2-seq-run workflow](https://support.10xgenomics.com/img/mkfastq-2.png "")](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/using/mkfastq#example_workflows)
> In this example, we have one 10x library sequenced on two flowcells. Note that after running cellranger mkfastq, we run a single instance of the pipeline on all the FASTQ files generated.

The common scenario of sequencing the same 'sequencing library' more than once (in the above example) is the reason why the 10x technicians are moving towards a FASTQ-level organization (rather than a 'sequencing library' a.k.a. 'pooled library' level).

# Proposed 10X Technician Spreadsheets: FASTQ, Sample, Library Features, Features
Below are proposed spreadsheets for use by the 10X techs (not all experiment-related columns are shown).

## FASTQ-Level Spreadsheet
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

## Sample-Level Spreadsheet
| Sample Name  | Loading Sample |  Sample Metadata ... | HTO | Expected Cell Number | Library Features |
|---|---|---|---|---|---|
| S1_GEX  | H1_GEX | ... | HTO-1  | 5000 | L-1 |

<!-- Difference b/t Sample name and Loading sample? -->
A CITE-seq sequencing-library will, in general, contain ADTs and HTOs. <!-- Should there be an ADTs column? -->
- `Sample Metadata`: will include necessary Cell Ranger information like organism, reference transcriptome, etc.
- `Library`: link to the [Library Features Table] below.
<!-- other column descriptions? -->

## Library Features Table
| Library | Feature | Index |
|---|---|---|
| L-1 | HTO-1 <!-- is this supposed to match the HTO column above? -->  | HTO-Index-1 |
| L-1 | CD8_HIMC-1_Lot-1  | ADT-Index-1 |
| … | …  | … |
| L-2 | CD3_HIMC-1_Lot-1  | ADT-Index-2 |
| L-2 | CD4_HIMC-1_Lot-1  | ADT-Index-3 |

Each library has a set of feature/index pairs associated with it, and these mappings are stored in the Library Features Table.

The `Feature` names contain the following underscore-delimited components:
1) official gene symbol of the measured protein (or the protein instead if desired - otherwise other names will be stored as aliases)
2) the unique HIMC id (e.g. HIMC-1), and the lot number (e.g. lot-1).

The `Index` column contains the oligo index IDs that can be looked up in [the `Features Table`][Library Features Table].

# 10x Required CSVs

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

| id | name | read | pattern | sequence | feature_type | target_gene_id (optional) | target_gene_name (optional) |
|---|---|---|---|---|---|---|---|
|   |   |   |   |   |   |   |   |
<!-- example row(s) -->

This document is only necessary for feature barcode (FBM) runs:
- `id`: unique id for the feature (can't collide with gene name)
- `name`: human readable feature name (e.g. gene name)
- `read`: specifies which sequencing read contains the sequence (e.g. R2)
- `pattern`: specifies how to extract seq from read
- `feature_type`: (e.g. custom <!-- more info? -->)
- `target_gene_id`, `target_gene_name`: optional, CRISPR-specific.

# `Processing-Run` Spreadsheets
Here we define a `Processing-Run` as a set of Cell Ranger jobs performed on one or more BCL files to obtain one or more FBMs and/or TCR/BCR sequence analysis.

A `Processing-Run` takes the spreadsheets below as inputs. They are similar to the spreadsheets that `cellranger mkfastq` and `count` take as inputs, but contain additional required arguments (e.g. expected cell count) as well as a layout of how to run the full `Processing-Run` set of jobs.

## 1. Custom Sheet CSV

| Lane| Sample | Index | Library Type | Reference Transcriptome | Number of Cells | Chemistry |
|---|---|---|---|---|---|---|
| 1  | S1_GEX | SI-GA-A3 | Gene Expression | GRCh38 | 3000 | 5-prime_V2 |

This CSV will be used to construct [the sample sheet CSV input for `mkfastq`][10X Sample Sheet CSV] as well as [the libraries CSV for `count`][10X Libraries CSV]. The last two columns will be used to construct additional arguments for `cellranger count`.

## 2. Feature Reference CSV (exactly as required by count)
The 10x techs will produce the feature reference CSV (presumably via lookup tables). <!-- more info? -->

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



[Library Features Table]: #library-features-table
[`Processing-Run`]: #processing-run-spreadsheets
[10X Sample Sheet CSV]: #sample-sheet-csv
[10X Libraries CSV]: #libraries-csv
