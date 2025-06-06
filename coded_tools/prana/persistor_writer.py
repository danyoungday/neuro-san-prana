# Copyright (C) 2023-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# neuro-san-demos SDK Software in commercial settings.
#
from typing import Any
from typing import Dict
from typing import Union

from neuro_san.interfaces.coded_tool import CodedTool
import pandas as pd


class PersistorWriterTool(CodedTool):
    """
    CodedTool implementation writes a {date, region, policy, and score} tuple to disk.
    Returns if the write was successful or not.
    """

    def __init__(self):
        """
        Constructs a PersistorWriter for the PRANA system.
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
                    "score" the score for the policy.
                    "notes" a brief summary of why the score was given.

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
        score: str = args.get("score", None)
        notes: str = args.get("notes", None)
        if date is None or region is None or policy is None or score is None or notes is None:
            return "Error: No date, region, policy, or score provided."

        # Parse date to datetime object
        try:
            date_parsed = pd.to_datetime(date)
        except ValueError as e:
            return f"Error: Failed to parse date {date}: {e}"

        # Create a new DataFrame with the provided data as a single row
        new_row = pd.DataFrame({
            "Date": [date_parsed],
            "Region": [region],
            "Policy": [policy],
            "Score": [score],
            "Notes": [notes.replace("\n", " ")]
        })

        # Append the new row to the existing DataFrame
        try:
            new_row.to_csv(self.persisted_path, mode="a", header=False, index=False)
        except Exception as e:
            return f"Error: Failed to write to file {self.persisted_path}: {e}"

        print(">>>>>>>>>>>>> Data written successfully >>>>>>>>>>>>>>>")

        return "Success: Data written to file."

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> str:
        """
        Delegates to the synchronous invoke method for now.
        """
        return self.invoke(args, sly_data)
