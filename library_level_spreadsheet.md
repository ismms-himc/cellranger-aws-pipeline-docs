# Library Level Spreadsheet
This document discusses proposed changes to the organization of sequencing run spreadsheets used by HIMC technicians running the 10x assay and the computational team performing pre-processing. This document heavily references the [10x documentation](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/using/mkfastq).

# Background
The relationship between **biological samples** (e.g. a cell suspension extracted from a single biological source (blood, tissue, etc)., see [glossary](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/glossary)), **sequencing libraries** (e.g. the end product from a 10x chip lane), **BCL files** (e.g. generally multiplexed from several sequencing libraries), and **Cell Ranger pre-processing runs** (e.g. can utilize several BCL files for a pooled run) can be complicated. 

### Two Samples, two Seq-Libraries, one Flowcell, two Counts
![alt text](https://support.10xgenomics.com/img/mkfastq-1.png "")

In this example, we have two 10x libraries (each processed through a separate Chromium chip channel) that are multiplexed on a single flowcell. Note that after running cellranger mkfastq, we run a separate instance of the pipeline on each library:

### Proposed Library-Level Spreadsheet
Laura is working on making a new sequencing-library-level spreadsheet. Below is the in-progress outline for this spreadsheet.

| Library  | Sample  | BCL  | Cell Ranger Run  |   
|---|---|---|---|
| L-1-GEX  | S-1  | BCL-1  | CR-1  |   
| L-1-ADT  | S-1  | BCL-1  | CR-1  |   
| L-1-HTO  | S-1  | BCL-1  | CR-1  |  
