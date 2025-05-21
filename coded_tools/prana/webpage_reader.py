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

import requests
from bs4 import BeautifulSoup
from neuro_san.interfaces.coded_tool import CodedTool


class WebPageReaderTool(CodedTool):
    """
    A coded tool that reads and extracts all visible text from a given webpage URL.
    """

    def __init__(self):
        """
        Constructs a WebPageReader for the PRANA system.
        """

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[str, Dict[str, Any]]:
        """
        :param args: An argument dictionary whose keys are the parameters
                to the coded tool and whose values are the values passed for them
                by the calling agent. This dictionary is to be treated as read-only.

                The argument dictionary expects the following keys:
                    "article_url" the url pointing to the news article the text is to be scraped from.

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
                The extracted text from the provided webpage.
            otherwise:
                A text string an error message in the format:
                "Error: <error message>"
        """
        article_url: str = args.get("article_url", None)
        if article_url is None:
            return "Error: No news url provided."
        print(">>>>>>>>>>>>>>>>>>> Extracting text >>>>>>>>>>>>>>>>>>")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"  # noqa E501
        }
        try:
            response = requests.get(article_url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            texts = soup.stripped_strings
            full_text = " ".join(texts)
            print(">>>>>>>>>>>>>>>>>>> Done! >>>>>>>>>>>>>>>>>>")
            return full_text
        except Exception as e:
            return f"Error: Unable to process the URL. {str(e)}"

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> str:
        """
        Delegates to the synchronous invoke method for now.
        """
        return self.invoke(args, sly_data)
