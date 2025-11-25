# osc-transformer-presteps

## 💬 Important

On June 26 2024, Linux Foundation announced the merger of its financial services umbrella, the Fintech Open Source Foundation (FINOS <https://finos.org>), with OS-Climate, an open source community dedicated to building data technologies, modelling, and analytic tools that will drive global capital flows into climate change mitigation and resilience; OS-Climate projects are in the process of transitioning to the FINOS governance framework <https://community.finos.org/docs/governance>; read more on finos.org/press/finos-join-forces-os-open-source-climate-sustainability-esg <https://finos.org/press/finos-join-forces-os-open-source-climate-sustainability-esg>_

|osc-climate-project| |osc-climate-slack| |osc-climate-github| |pypi| |pdm| |PyScaffold| |OpenSSF Scorecard|

## Overview

CLI utilities to:  
Extract `text/structure` from PDFs into JSON.  
Curate a labeled training dataset (CSV) from extracted JSON + human annotations + KPI mapping.  
Intended to feed downstream transformer models (relevance detector and KPI detector) used by osc-transformer-based-extractor.  
Works stand-alone for PDF JSON extraction and for dataset curation.  

## Prerequisites

**OS:** Linux (commands below assume bash)  
**Python:** 3.12  
**Recommended:** run inside a virtual environment  
**Disk space:** enough for your PDFs, extracted JSON, logs, and curated CSV  

## Installation

### From PyPI (recommended for this tool):
```
python3.12 -m venv venv_presteps
source venv_presteps/bin/activate
pip install --upgrade pip
pip install osc-transformer-presteps
deactivate
```

Demo materials If you want to use the demo inputs that ship with the repo:  

### Clone just to copy demo inputs (optional)
```
git clone https://github.com/os-climate/osc-transformer-presteps.git
```

### Create a working/demo folder structure
```
mkdir -p demo/extraction/input
mkdir -p demo/extraction/output
mkdir -p demo/extraction/log
mkdir -p demo/curation/input
mkdir -p demo/curation/output
mkdir -p demo/curation/log
```

### Copy demo inputs

```
cp -r osc-transformer-presteps/demo/extraction/input demo/extraction/
cp -r osc-transformer-presteps/demo/curation/input demo/curation/
```

## Quickstart 

1.	Activate the environment:
```
source venv_presteps/bin/activate
```

2. Extract PDF(s) to JSON:

	- Input folder contains one or more PDF files.  
	- Output folder will receive one JSON per input PDF.  
	- Logs folder will receive log files.  
```
cd demo/extraction
osc-transformer-presteps extraction run-local-extraction \
  "input/" \
  --output-folder="output/" \
  --logs-folder="log/" \
  --force
```

**Notes:**

```--force``` can attempt extraction from restricted PDFs. Ensure this is legal for your use case.  
Typical output example: ```demo/extraction/output/Test_output.json```

3. Curate a training dataset for the relevance detector:

**Requires:**  
	- Extracted JSON file(s)  
	- An annotation file (xlsx)  
	- A KPI mapping file (csv)  
```
cd ../curation
```

**Example:** bring one extracted JSON into curation input
```
cp ../extraction/output/Test_output.json `input/`
osc-transformer-presteps relevance-curation run-local-curation \
  --create_neg_samples \
  "input/Test_output.json" \
  "input/test_annotations.xlsx" \
  "input/kpi_mapping.csv" \
  "output/"
```

**Outputs**

A CSV named Curated_dataset.csv containing labeled samples for training.  
Known issue: Current version may ignore the output folder flag and write `Curated_dataset.csv` into the current working directory. If you don’t see it inside your specified `output/`, check the working directory.  


4. Deactivate the environment

```deactivate```

## Command reference

### PDF Extraction
```
osc-transformer-presteps extraction run-local-extraction \
  <input_folder> \
  --output-folder=<path> \
  --logs-folder=<path> \
  [--force]
```

**Arguments:**  

`:` directory with PDF files.

`--output-folder:` where JSON files are written.

`--logs-folder:` where logs are written.

`--force:` attempt extraction from encrypted PDFs (use responsibly).


## Relevance Curation
```
osc-transformer-presteps relevance-curation run-local-curation \
  [--create_neg_samples] \
  <extracted_json_file> \
  <annotations_file.xlsx> \
  <kpi_mapping.csv> \
  <output_folder>
```

### Arguments:

: a JSON produced by the extraction step.  
: human annotations. See “Input file formats” below.  
: KPI definitions. See “Input file formats” below.  
: target folder for outputs (note: current version may ignore and write to CWD). Options:  
`--create_neg_samples`: generate negative examples (non-relevant samples) in the curated dataset.  

### Input file formats (for curation)

#### KPI mapping CSV (example columns):
`kpi_id`: unique KPI identifier   
`question`: the question/indicator to extract  
`sectors`: applicable sectors (e.g., "OG, CM, CU")  
`add_year`: TRUE/FALSE to add year  
`kpi_category`: data type/category (e.g., TEXT)  

#### Annotation XLSX (example columns):
`company`: company name  
`source_file`: original document filename  
`source_page`: page numbers  
`kpi_id`: KPI identifier aligned to mapping  
`year`: year referenced  
`answer`: extracted answer text/value  
`data_type`: e.g., TEXT or TABLE  
`relevant_paragraphs`: supporting text/section(s)  
`annotator`: who annotated  
`sector`: applicable sector  

## Folder structure example
```
your-project/  
├─ venv_presteps/  
├─ demo/  
│  ├─ extraction/  
│  │  ├─ input/                  # PDFs here  
│  │  ├─ output/                 # JSON output here  
│  │  └─ log/  
│  └─ curation/  
│     ├─ input/  
│     │  ├─ Test_output.json     # from extraction  
│     │  ├─ test_annotations.xlsx  
│     │  └─ kpi_mapping.csv  
│     ├─ output/                 # may be ignored by current version  
│     └─ log/  
```
## Troubleshooting and tips

**Curated_dataset.csv not in `output/`:** Known issue — the tool may write to the current working directory instead of the specified output folder. Check your CWD.  
**Paths on Windows: ** If you run on Windows, adapt path separators accordingly.  
**Permissions:** If you see permission errors writing logs or outputs, ensure the directories exist and are writable.  
**Force flag legality:** Using ```--force``` to bypass PDF restrictions may not be legal in some jurisdictions; ensure compliance. 
 
## Verify success:  
**Extraction:** JSON files present in `output/` and non-empty logs.  
**Curation:** Curated_dataset.csv generated and contains expected rows/columns.  

## Development (optional)
 If you plan to develop or explore internals, the upstream repo provides demos and a PDM/pytest setup:  
```
git clone https://github.com/os-climate/osc-transformer-presteps
cd osc-transformer-presteps
pip install pdm tox
pdm sync
tox -e lint
tox -e test
```

## License and governance

This project is part of the OS-Climate ecosystem. Please consult the repository for license and governance details.
