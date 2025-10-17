import subprocess
import os
import re
from pathlib import Path
from tqdm import tqdm

def run_claim_extraction(input_dir, data_dir, model_name, image):
    input_dir = Path(input_dir)
    data_dir = Path(data_dir)
    
    # Derive the folder name for the model
    # e.g. meta-llamaLlama-3.1-8B-Instruct from the input_dir path
    model_folder = input_dir.name  # last part of input path
    clean_model_name = re.sub(r'[\\/]', '', model_folder)  # remove slashes just in case

    # Create output directory
    output_dir = data_dir / "claims_input_files" / clean_model_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Iterate over all input files
    files = sorted(input_dir.glob("*.jsonl"))
    print(f"Found {len(files)} input files in {input_dir}")

    for file_path in tqdm(files, desc=f"Extracting claims for {clean_model_name}"):
        print(f"Processing {file_path.name}")

        cmd = [
            "srun", "-K",
            "--job-name=veriscore-claim-extraction",
            "--partition=A100-40GB,A100-80GB,A100-PCI,RTXA6000,RTXA6000-SLT,RTX3090",
            "--nodes=1",
            "--ntasks=1",
            "--mem=128G",
            "--cpus-per-task=4",
            "--gpus-per-task=1",
            f"--container-image={image}",
            f"--container-workdir={os.getcwd()}",
            f"--container-mounts=/netscratch/$USER:/netscratch/$USER,/ds:/ds:ro,{os.getcwd()}:{os.getcwd()}",
            "python3", "-m", "veriscore.extract_claims",
            "--data_dir", str(data_dir),
            "--input_file", str(file_path),
            "--output_dir", str(output_dir),  # save results here
            "--model_name", model_name,
            "--use_external_model"
        ]

        subprocess.run(cmd, check=True)

if __name__ == "__main__":
    run_claim_extraction(
        input_dir="./data/input_files/meta-llamaLlama-3.1-8B-Instruct",
        data_dir="./data",
        model_name="SYX/mistral_based_claim_extractor",
        image="/netscratch/abu/images/veriscore.sqsh"
    )

