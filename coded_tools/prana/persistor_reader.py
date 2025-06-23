# Copyright (C) 2023-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# neuro-san-demos SDK Software in commercial settings.
#
import json
from typing import Any
from typing import Dict
from typing import Union

from neuro_san.interfaces.coded_tool import CodedTool
import pandas as pd


class PersistorReaderTool(CodedTool):
    """
    CodedTool implementation loads previously persisted {date, region, policy, score, notes} tuples from disk.
    Returns the JSON object as a dictionary.
    """

    def __init__(self):
        """
        Constructs a PersistorReader for the PRANA system.
        """
        self.persisted_path = "data/persistence.csv"

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[str, Dict[str, Any]]:
        """
        :param args: An argument dictionary whose keys are the parameters
                to the coded tool and whose values are the values passed for them
                by the calling agent. This dictionary is to be treated as read-only.

                The argument dictionary expects the following keys:
                    "date" the date.
                    "region" the region.
                    "policy" the policy being measured.

        :param sly_data: A dictionary whose keys are defined by the agent hierarchy,
                but whose values are meant to be kept out of the chat stream.

                This dictionary is largely to be treated as read-only.
                It is possible to add key/value pairs to this dict that do not
                yet exist as a bulletin board, as long as the responsibility
                for which coded_tool publishes new entries is well understood
                by the agent chain implementation and the coded_tool implementation
                adding the data is not invoke()-ed more than once.

                Keys expected for this implementation are:
                    None

        :return:
            In case of successful execution:
                A string of persisted data in the format:
                    "date:<date>, region:<region>, policy:<policy>, score:<score>"
                with new entries on each line.
            otherwise:
                A text string an error message in the format:
                "Error: <error message>"
        """
        date: str = args.get("date", None)
        region: str = args.get("region", None)
        policy: str = args.get("policy", None)
        if date is None or region is None or policy is None:
            return "Error: No date, region, or policy provided."

        # Parse date to datetime object
        try:
            date_parsed = pd.to_datetime(date)
        except ValueError as e:
            return f"Error: Failed to parse date {date}: {e}"

        # Filter the DataFrame based on the provided date, region, and policy
        df = pd.read_csv(self.persisted_path)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        filtered_df = df
        if len(filtered_df) >= 3:
            filtered_df = filtered_df.iloc[-3:]
        # TODO: This is commented out because right now all our data is relevant so we can retrieve it all without the
        # point of failure of not filtering right.
        # filtered_df = df[
        #     (df["date"] <= date_parsed) & (df["region"] == region) & (df["policy"] == policy)
        # ]

        print(f"---------------- Found {len(filtered_df)} rows ----------------")

        if len(filtered_df) == 0:
            return f"No data found for date {date}, region {region}, policy {policy}."

        # Return a JSON formatted string
        filtered_df = filtered_df.astype(str)
        json_formatted = {"region": region, "policy": policy, "historical_data": []}
        for _, row in filtered_df.iterrows():
            json_formatted["historical_data"].append({
                "date": row["Date"],
                "score": row["Score"],
                "notes": row["Notes"]
            })
        return json.dumps(json_formatted, indent=4)

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> str:
        """
        Delegates to the synchronous invoke method for now.
        """
        return self.invoke(args, sly_data)


if __name__ == "__main__":
    tool = PersistorReaderTool()
    print(tool.invoke({"date": "", "region": "", "policy": ""}, {}))
