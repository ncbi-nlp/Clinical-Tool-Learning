## Step 0: Preprocess the admission notes from MIMIC-III 

To run AgentMD on the MIMIC-III admission notes, one needs to first download the MIMIC-III dataset from PhysioNet (https://physionet.org/content/mimiciii/1.4/), which requires certain training and data usage agreement set by the data owner.

Then one needs to process the MIMIC-III data using https://github.com/bvanaken/clinical-outcome-prediction. Specifically, go to the directory and run:

```bash
python tasks/mp/mp.py \
 --mimic_dir ${MIMIC_DIR} \   # required
 --save_dir ${DIR_TO_SAVE_DATA} \   # required
 --admission_only True \   # required
```

Please then move the processed test split under the `data` directory here:

```bash
mv ${DIR_TO_SAVE_DATA}/MP_IN_adm_test.csv dataset/test.csv
```

## Step 1: Risk triage 

The first step is to triage the patient into different risks by AgentMD. Please run:

```bash
python step1_risk_triage.py
```

The default backbone LLM is GPT-4, and the results will be saved in `results/file1_patient_risks.json`. 

## Step 2: Calculator retrieval 

After triaging, the second step is to retrieve the relevant tools for each risk. Please run (note that this step requires GPU for using the dense retriever):

```bash
python step2_tool_retrieval.py 
```

The calculator retrieval results will be saved in `results/file2_patient_risk_tools.json`.

## Step 3: Calculator selection

The third step is to select eligible calculators from the retrieved candidates. Please run:

```bash
python step3_tool_selection.py
```

The selected calculators will be saved in `results/file3_patient_tool_selection.json`.

## Step 4: Calculator computation

After selecting the tools, AgentMD will conduct the computation for the given patient. Please run:

```bash
python step4_tool_using.py 
```

The computation results will be saved in `results/file4_patient_tool_results.json`
