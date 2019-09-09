# Library Level Spreadsheet
This document discusses proposed changes to the organization of sequencing run spreadsheets used by HIMC technicians running the 10x assay and the computational team performing pre-processing. This document heavily references the [10x documentation](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/using/mkfastq).

# Background
The relationship between **biological samples** (e.g. a cell suspension extracted from a single biological source (blood, tissue, etc)., see [glossary](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/glossary)), **sequencing libraries** (e.g. the end product from a 10x chip lane), **BCL files** (e.g. generally multiplexed from several sequencing libraries), **FASTQs** (e.g. the product of de-multiplexing BCL files, sub-divided by lane and read) and **Cell Ranger pre-processing runs** (e.g. can utilize several BCL files for a pooled run) can be complicated. Two examples from the documentation are shown below.

An additional common scenario is sequencing the same 'sequencing library' more than once. This is the reason why the 10x technicians are moving towards a FASTQ level organization (rather than a 'sequencing library' level).

### 2 Samples, 2 Seq-Libraries, 1 Seq-Run/Flowcell, 2 FBMs (Feature barcode matrices)
![alt text](https://support.10xgenomics.com/img/mkfastq-1.png "")

"In this example, we have two 10x libraries (each processed through a separate Chromium chip channel) that are multiplexed on a single flowcell. Note that after running cellranger mkfastq, we run a separate instance of the pipeline on each library"

### 1 Sample, 2 Seq-Libraries, 2 Seq-Run/Flowcells, 1 FBM
![alt text](https://support.10xgenomics.com/img/mkfastq-2.png "")
"In this example, we have one 10x library sequenced on two flowcells. Note that after running cellranger mkfastq, we run a single instance of the pipeline on all the FASTQ files generated"

### Proposed Library-Level Spreadsheet
Laura is working on making a new seq-library-level spreadsheet. Below is the in-progress outline for this spreadsheet along with some example configurations

| Library  | Sample  | BCL  | Cell Ranger Run  |   
|---|---|---|---|
| S1_GEX  | S1  | BCL-1  | CR-1  |   
| S2_GEX  | S2  | BCL-1  | CR-1  |   
| S3_GEX  | S3  | BCL-1  | CR-1  |  

### scRNA-seq: 3 Samples, 3 10x Lanes, 3 Seq-Libraries, 1 Flowcell/BCL
These three rows represents an experiment (e.g. Cell Ranger Run `CR-1`) that has three samples (`S1`, `S2`, `S3`) run in separate 10x chip lanes. The three libraries generated from the three lanes are multiplexed and run in a single flowcell, which generates a single BCL file (`BCL-1`). This single BCL file will need to be de-multiplexed, producing three sets of FASTQs that will produce three 
-barcode-matrices (FBMs). 

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
|---|---|---|---| -- |
| S_GEX  | S4_S5  | BCL-2  | CR-2  |   |
| S_ADT  | S4_S5  | BCL-2  | CR-2  |   |
| S_HTO  | S4_S5  | BCL-2  | CR-2  |    |

```   
mkfastq              count     de-hashtag
BCL-2 -> FASTQs_GEX -> FBM -> FBM_S4
      -> FASTQs_ADT           FBM_S5
      -> FASTQs_HTO    
```

### scRNA-seq (pooled run): One Sample, Three Seq-Libraries, Three Flowcell/BCLs

| Library  | Sample  | BCL  | Cell Ranger Run  |   
|---|---|---|---| 
| S6_GEX_A  | S6  | BCL-3  | CR-3  |
| S6_GEX_B  | S6  | BCL-4  | CR-3  |   
| S6_GEX_C  | S6  | BCL-5  | CR-3  |  




