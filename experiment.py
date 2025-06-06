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


def run_experiment(wandb_data_path: str, log_dir: str, wandb_params: dict, force: bool = False):
    """
    Runs the experiment generating a dataset using PRANA.
    """
    # Check if the persistence file exists
    if os.path.exists("data/persistence.csv") and not force:
        inp = input("Persistence file exists. Do you want to overwrite? (y/n):")
        if inp.lower() != "y":
            print("Exiting...")
            return

    # Check if the log directory exists
    if os.path.exists(log_dir):
        if not force:
            inp = input(f"Log directory {log_dir} exists. Do you want to overwrite? (y/n):")
            if inp.lower() != "y" and not force:
                print("Exiting...")
                return
        shutil.rmtree(log_dir)
    os.makedirs(log_dir)

    # wandb setup
    run = wandb.init(
        **wandb_params
    )
    # log hocon
    config_artifact = wandb.Artifact(name="hocon", type="config")
    config_artifact.add_file("registries/prana.hocon")
    run.log_artifact(config_artifact)

    # log knowdocs
    docs_artifact = wandb.Artifact(name="knowdocs", type="knowdocs")
    for file in os.listdir("coded_tools/prana/knowdocs"):
        docs_artifact.add_file(os.path.join("coded_tools/prana/knowdocs", file))
    run.log_artifact(docs_artifact)

    # log code
    run.log_code(name="prana-code", include_fn=code_include_fn)

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
    persistence.to_csv("data/persistence.csv", index=False, header=True)

    # Load data and run experiment on it
    data_dir = run.use_artifact(wandb_data_path.split("/")[0], type="dataset").download(root="data/artifacts")
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

    # Save results in wandb
    results_df = pd.read_csv("data/persistence.csv")
    table = wandb.Table(dataframe=results_df)
    wandb.log({"results": table})

    logs_artifact = wandb.Artifact(name="neuro-san-logs", type="logs")
    for log_path in os.listdir(log_dir):
        logs_artifact.add_file(os.path.join(log_dir, log_path))
    wandb.log_artifact(logs_artifact)

    # Copy results file to log directory locally
    shutil.copy2("data/persistence.csv", os.path.join(log_dir, "persistence.csv"))

    run.finish()

if __name__ == "__main__":
    # run_experiment(wandb_data_path="england-dataset:latest/england-dataset.csv",
    #                log_dir="logs/four-one",
    #                wandb_params={"project": "prana", "name": "four-one"},
    #                force=True)

    for i in range(10):
        run_experiment(wandb_data_path="england-dataset:latest/england-dataset.csv",
                       log_dir=f"logs/four-one-repeat-{i}",
                       wandb_params={"project": "prana", "name": f"four-one-repeat-{i}"},
                       force=True)
