"""
Script used to create a dataset from the OxCGRT raw data.
"""
import re

import pandas as pd
import wandb


def extract_urls(row: pd.Series) -> list[str]:
    """
    Extracts URLs from a subset of columns in a DataFrame row.
    """
    urls = []
    for col in row.index:
        text = row[col]
        if not pd.isna(text):
            url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
            urls.extend(re.findall(url_pattern, text))
    if len(urls) == 0:
        return pd.NA
    urls_str = ", ".join(urls)
    return urls_str


def create_dataset(data_paths: list[str],
                   location_filter: dict[str, str],
                   policy_cols: list[str],
                   save_path: str = None) -> pd.DataFrame:
    """
    Creates a dataset from the OxCGRT data.
        1. Merge all csvs together
        2. Sort by date
        3. Filter by location
        4. Remove rows where there is no note and score for any given policy
        5. Extract URLs from notes and drop rows with no URLs
        6. Fill nan policy scores with the previous valid score, if there is no previous score fill with 0

    location filter: dict of column name to value example:
        CountryName: United Kingdom
        RegionName: England
    policy cols are a subset of:
        C1E_School closing
        C2E_Workplace closing
        C3E_Cancel public events
        C4E_Restrictions on gatherings
        C5E_Close public transport
        C6E_Stay at home requirements
        C7E_Restrictions on internal movement
        C8E_International travel controls
    """
    dfs = []
    for path in data_paths:
        dfs.append(pd.read_csv(path))
    df = pd.concat(dfs, ignore_index=True)

    df["Date"] = pd.to_datetime(df["Date"], format="%Y%m%d")
    df = df.sort_values(by=["Date"])

    for col, val in location_filter.items():
        df = df[df[col] == val]

    notes_cols = [policy[:2] + "_Notes" for policy in policy_cols]
    flag_cols = [policy.split("_")[0] + "_Flag" for policy in policy_cols]
    flag_cols = [col for col in flag_cols if col in df.columns]
    index_cols = ["Date", "CountryName", "RegionName", "Jurisdiction"]

    df = df.dropna(subset=notes_cols, how="all")
    df = df.dropna(subset=policy_cols, how="all")

    # Extract URLs from notes columns
    source_cols = [f"{policy.split("_")[0]}_Source" for policy in notes_cols]
    for notes_col, source_col in zip(notes_cols, source_cols):
        df[source_col] = df[[notes_col]].apply(extract_urls, axis=1)
    # Get rid of rows with no URLs
    df = df.dropna(subset=source_cols, how="all")

    # Fill nan policy scores with the previous valid score
    # If there is no previous valid score, assume there is no policy in effect and fill with 0
    for policy_col in policy_cols:
        df[policy_col] = df[policy_col].ffill()
        df[policy_col] = df[policy_col].fillna(0)

    dataset = df[index_cols + policy_cols + flag_cols + notes_cols + source_cols + ["ConfirmedCases"]].copy()
    if save_path is not None:
        dataset.to_csv(save_path, index=False)
    return dataset


def update_artifact(artifact_name: str, file_paths: list[str]):
    """
    Updates a wandb artifact with the given name using the provided files.
    """
    run = wandb.init(project="prana", name=f"update-{artifact_name}", job_type="add-dataset")
    artifact = wandb.Artifact(name=artifact_name, type="dataset")
    for path in file_paths:
        artifact.add_file(path)
    artifact.save()
    run.finish()


def main():
    """
    Creates a dataset and updates the artifact in wandb.
    """
    save_path = "data/australia-dataset.csv"
    policy_cols = ["C1E_School closing",
                   "C2E_Workplace closing",
                   "C3E_Cancel public events",
                   "C4E_Restrictions on gatherings",
                   "C5E_Close public transport",
                   "C6E_Stay at home requirements",
                   "C7E_Restrictions on internal movement",
                   "C8E_International travel controls"]
    location_filter = {"CountryName": "Australia"}
    data_paths = [f"data/raw/OxCGRT_fullwithnotes_national_{year}_v1.csv" for year in [2020, 2021, 2022]]
    create_dataset(data_paths, location_filter, policy_cols, save_path)
    update_artifact("australia-dataset", ["data/australia-dataset.csv"])


if __name__ == "__main__":
    main()
