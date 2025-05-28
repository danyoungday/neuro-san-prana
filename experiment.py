"""
Runs the experiment to generate a dataset using prana
"""
import os
import shutil

from neuro_san.client.agent_session_factory import AgentSessionFactory
from neuro_san.client.streaming_input_processor import StreamingInputProcessor
import pandas as pd
from tqdm import tqdm


def prompt_format(row: pd.Series) -> str:
    """
    Formats a row of the dataframe into a prompt string.
    """
    prompt = f"Score the policy {row['Policy']}"
    prompt += f" on {row['Date']}"
    prompt += f" for region {row['Region']}"
    prompt += f" using news articles: {row['Source']}"
    return prompt


def run_experiment(data_path: str, log_dir: str, force: bool = False):
    """
    Runs the experiment generating a dataset using PRANA.
    """
    # Check if the persistence file exists
    if os.path.exists("data/persistence.csv"):
        inp = input("Persistence file exists. Do you want to overwrite? (y/n):")
        if inp.lower() != "y" and not force:
            print("Exiting...")
            return

    # Check if the log directory exists
    if os.path.exists(log_dir):
        inp = input(f"Log directory {log_dir} exists. Do you want to overwrite? (y/n):")
        if inp.lower() != "y" and not force:
            print("Exiting...")
            return
        shutil.rmtree(log_dir)
    os.makedirs(log_dir)

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
                                              thinking_dir=log_dir)

    # Clear results file
    persistence = pd.DataFrame(columns=["Date", "Region", "Policy", "Score", "Notes"])
    persistence.to_csv("data/persistence.csv", index=False, header=True)

    # Load data and run experiment on it
    df = pd.read_csv(data_path)
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

    shutil.copy2("data/persistence.csv", os.path.join(log_dir, "persistence.csv"))


if __name__ == "__main__":
    # run_experiment("data/texas-smaller.csv", "logs/temp")
    for i in range(10):
        run_experiment("data/texas-smaller.csv", f"logs/repeated/repeat-{i}", force=True)
