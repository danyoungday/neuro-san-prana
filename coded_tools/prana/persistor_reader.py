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


class PersistorReaderTool(CodedTool):
    """
    CodedTool implementation loads previously persisted {date, region, criteria, and score} tuples from disk.
    Returns the JSON object as a dictionary.
    """

    def __init__(self):
        """
        Constructs a PersistorReader for the PRANA system.
        """
        self.persisted_path = "data/ox/persistence.csv"

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[str, Dict[str, Any]]:
        """
        :param args: An argument dictionary whose keys are the parameters
                to the coded tool and whose values are the values passed for them
                by the calling agent. This dictionary is to be treated as read-only.

                The argument dictionary expects the following keys:
                    "date" the date.
                    "region" the region.
                    "criteria" the criteria being measured.

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
                    "date:<date>, region:<region>, criteria:<criteria>, score:<score>, source:<source>"
                with new entries on each line.
            otherwise:
                A text string an error message in the format:
                "Error: <error message>"
        """
        date: str = args.get("date", None)
        region: str = args.get("region", None)
        criteria: str = args.get("criteria", None)
        if date is None or region is None or criteria is None:
            return "Error: No date, region, or criteria provided."

        # Parse date to datetime object
        try:
            date_parsed = pd.to_datetime(date)
        except ValueError as e:
            return f"Error: Failed to parse date {date}: {e}"

        # Filter the DataFrame based on the provided date, region, and criteria -> convert to string
        df = pd.read_csv(self.persisted_path)
        filtered_df = df[
            (df["date"] <= date_parsed) & (df["region"] == region) & (df["criteria"] == criteria)
        ]
        filtered_df = filtered_df.astype(str)

        # Parse each row into the string we're going to return to the LLM
        response = ""
        n_rows = 0
        for _, row in filtered_df.iterrows():
            response += f"date:{row['date']}, region:{row['region']}, criteria:{row['criteria']}, score:{row['score']}, source:{row['source']}\n"  # noqa: E501
            n_rows += 1

        print(f"---------------- Found {n_rows} rows ----------------")

        # If no rows were found, return a string saying so
        if response == "":
            return f"No data found for date {date}, region {region}, criteria {criteria}."

        # Return the response string
        return response.strip()

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> str:
        """
        Delegates to the synchronous invoke method for now.
        """
        return self.invoke(args, sly_data)
