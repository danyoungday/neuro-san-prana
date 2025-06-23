"""
Runs the experiment to generate a dataset using prana
"""
import os
import shutil

from neuro_san.client.agent_session_factory import AgentSessionFactory
from neuro_san.client.streaming_input_processor import StreamingInputProcessor
import pandas as pd
from tqdm import tqdm
import wandb
from wandb.sdk.wandb_run import Run
import yaml


PERSISTENCE_FILE_PATH = "data/persistence.csv"
HOCON_FILE_PATH = "registries/prana.hocon"


def prompt_format(row: pd.Series) -> str:
    """
    Formats a row of the dataframe into a prompt string.
    """
    prompt = f"Score the policy {row['Policy']}"
    prompt += f" on {row['Date']}"
    prompt += f" for region {row['Region']}"
    prompt += f" using news articles: {row['Source']}"
    return prompt


def code_include_fn(path: str, _: str) -> bool:
    """
    Function used by wandb to determine if a code file should be uploaded.
    """
    if "coded_tools/prana" in path and path.endswith(".py"):
        return True
    if "experiment.py" in path:
        return True
    return False


def clean_up(log_dir: str, force: bool) -> bool:
    """
    Cleans up the project. Clears persistence file and log directory.
    Returns False if the user wants to exit the program, true otherwise.
    """
    # Check if the persistence file exists
    if os.path.exists(PERSISTENCE_FILE_PATH) and not force:
        inp = input("Persistence file exists. Do you want to overwrite? (y/n):")
        if inp.lower() != "y":
            print("Exiting...")
            return False

    # Check if the log directory exists
    if os.path.exists(log_dir):
        if not force:
            inp = input(f"Log directory {log_dir} exists. Do you want to overwrite? (y/n):")
            if inp.lower() != "y" and not force:
                print("Exiting...")
                return False
        shutil.rmtree(log_dir)
    os.makedirs(log_dir)
    return True


def get_wandb_artifact(run: Run,
                       new_file_paths: list[str],
                       artifact_path: str,
                       artifact_type: str,
                       download_root: str) -> wandb.Artifact:
    """
    Gets a wandb artifact. If any of our new files are different from the old ones, we update the artifact.
    Then we return the artifact whether it was updated or not.
    """
    # Download the old artifact
    api = wandb.Api()
    old_hocon_path = api.artifact(artifact_path, type=artifact_type).download(root=download_root)

    # Set up the artifact to be saved to.
    artifact_name = artifact_path[artifact_path.find("/")+1:artifact_path.find(":")]
    artifact = wandb.Artifact(name=artifact_name, type=artifact_type)

    # See if we need to update the artifact. If there are any new files or an old file doesn't match, we have to update.
    update_artifact = False
    for new_file_path in new_file_paths:
        assert os.path.exists(new_file_path), f"New file path {new_file_path} does not exist."
        old_file_path = os.path.join(old_hocon_path, os.path.basename(new_file_path))
        if not os.path.exists(old_file_path):
            print(f"file {old_file_path} does not exist in the old artifact, adding it.")
            update_artifact = True
            break
        else:
            with open(old_file_path, "r", encoding="utf-8") as old_f:
                with open(new_file_path, "r", encoding="utf-8") as new_f:
                    if old_f.read() != new_f.read():
                        print(f"file {old_file_path} does not match the new file {new_file_path}, updating.")
                        update_artifact = True
                        break

    if update_artifact:
        print("Updating artifact:", artifact_path)
        # Add the new files to the artifact and save
        for new_file_path in new_file_paths:
            artifact.add_file(new_file_path)
        artifact.save()

    # Retrieve the artifact, whether it was updated or not
    artifact = run.use_artifact(artifact_path, type=artifact_type)
    return artifact


def wandb_setup(wandb_params: dict, wandb_data_path: str) -> tuple[Run, dict[str, wandb.Artifact]]:
    """
    Sets up the wandb run, creates necessary input artifacts, and logs the code.
    Returns a run object and dictionary of artifacts.
    """    
    run = wandb.init(**wandb_params)

    config_artifact = get_wandb_artifact(run,
                                         new_file_paths=[HOCON_FILE_PATH],
                                         artifact_path="prana/hocon:latest",
                                         artifact_type="config",
                                         download_root="data/artifacts/hocon")

    knowdocs_paths = [os.path.join("coded_tools/prana/knowdocs", f) for f in os.listdir("coded_tools/prana/knowdocs")]
    knowdocs_artifact = get_wandb_artifact(run,
                                           new_file_paths=knowdocs_paths,
                                           artifact_path="prana/knowdocs:latest",
                                           artifact_type="knowdocs",
                                           download_root="data/artifacts/knowdocs")

    data_artifact = run.use_artifact(wandb_data_path.split("/")[0], type="dataset")

    run.log_code(name="prana-code", include_fn=code_include_fn)

    return run, {"config": config_artifact, "knowdocs": knowdocs_artifact, "data": data_artifact}


def wandb_cleanup(run: Run, log_dir: str):
    """
    Cleans up the run by logging the artifacts and finishing the run.
    """
    # Save results in wandb
    results_df = pd.read_csv(PERSISTENCE_FILE_PATH)
    table = wandb.Table(dataframe=results_df)
    run.log({"results": table})

    logs_artifact = wandb.Artifact(name="neuro-san-logs", type="logs")
    for log_path in os.listdir(log_dir):
        logs_artifact.add_file(os.path.join(log_dir, log_path))
    run.log_artifact(logs_artifact)

    run.finish()


def run_experiment(wandb_data_path: str, log_dir: str, wandb_params: dict, force: bool = False):
    """
    Runs the experiment generating a dataset using PRANA.
    """
    # Clean up the project
    if not clean_up(log_dir, force):
        return

    run, artifacts_dict = wandb_setup(wandb_params, wandb_data_path)

    # Set up the neuro-san stuff
    factory = AgentSessionFactory()
    session = factory.create_session(session_type="grpc",
                                     agent_name="prana",
                                     hostname="localhost",
                                     port=30011,
                                     use_direct=False,
                                     metadata={})
    input_processor = StreamingInputProcessor(default_input="DEFAULT",
                                              session=session,
                                              thinking_file="logs/thinking.txt",
                                              thinking_dir=log_dir)

    # Clear results file
    persistence = pd.DataFrame(columns=["Date", "Region", "Policy", "Score", "Notes"])
    persistence.to_csv(PERSISTENCE_FILE_PATH, index=False, header=True)

    # Load data and run experiment on it
    data_dir = artifacts_dict["data"].download(root=f"data/artifacts/{wandb_data_path.split('/')[0]}")
    df = pd.read_csv(os.path.join(data_dir, wandb_data_path.split("/")[1]))
    for _, row in tqdm(df.iterrows(), desc="Processing rows", total=len(df)):
        prompt = prompt_format(row)

        state = {
            "last_chat_response": None,
            "prompt": "Please enter your response ('quit' to terminate):\n",
            "timeout": 5000,
            "num_input": 0,
            "user_input": prompt,
            "sly_data": {},
            "chat_filter": {"chat_filter_type": "MAXIMAL"},
        }

        input_processor.process_once(state)

    wandb_cleanup(run, log_dir)

    # Copy results file to log directory locally
    shutil.copy2(PERSISTENCE_FILE_PATH, os.path.join(log_dir, "persistence.csv"))


if __name__ == "__main__":
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    run_experiment(wandb_data_path=config['wandb_data_path'],
                   log_dir=f"logs/{config['name']}",
                   wandb_params={"project": "prana", "name": config['name']},
                   force=True)
