"""
Runs the experiment to generate a dataset using prana
"""
import os

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


def run_experiment(data_path: str):
    """
    Runs the experiment generating a dataset using PRANA.
    """
    # Check if the persistence file exists
    if os.path.exists("data/persistence.csv"):
        inp = input("Persistence file exists. Do you want to overwrite? (y/n):")
        if inp.lower() != "y":
            print("Exiting...")
            return

    # Set up the neuro-san stuff
    factory = AgentSessionFactory()
    session = factory.create_session(session_type="grpc",
                                     agent_name="prana",
                                     hostname="localhost",
                                     port=30011,
                                     use_direct=False,
                                     metadata={})

    input_processor = StreamingInputProcessor(default_input="DEFAULT",
                                              thinking_file="thinking.txt",
                                              session=session,
                                              thinking_dir="logs/")

    # Clear results file
    persistence = pd.DataFrame(columns=["Date", "Region", "Policy", "Score", "Notes"])
    persistence.to_csv("data/persistence.csv", index=False, header=True)

    # Load data and run experiment on it
    df = pd.read_csv(data_path)
    for i, row in tqdm(df.iterrows(), desc="Processing rows", total=len(df)):
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


if __name__ == "__main__":
    run_experiment("data/texas.csv")
