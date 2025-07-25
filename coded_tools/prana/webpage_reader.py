# Copyright (C) 2023-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# neuro-san-demos SDK Software in commercial settings.
#
from io import BytesIO
import time
from typing import Any
from typing import Dict
from typing import Union

import requests
from bs4 import BeautifulSoup
from neuro_san.interfaces.coded_tool import CodedTool
from pypdf import PdfReader


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
                    "news_url" the url pointing to the news article the text is to be scraped from.

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
        news_url: str = args.get("article_url", None)
        if news_url is None:
            return "Error: No news url provided."
        print(">>>>>>>>>>>>>>>>>>> Extracting text >>>>>>>>>>>>>>>>>>")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"  # noqa E501
        }
        if news_url.endswith(".pdf"):
            try:
                text = self.read_pdf(news_url, headers)
                print(">>>>>>>>>>>>>>>>>>> Extracted pdf >>>>>>>>>>>>>>>>>>")
                return text
            except Exception as e:
                return f"Error: Failed to fetch the PDF. {str(e)}"
        else:
            try:
                text = self.read_html(news_url, headers)
                print(">>>>>>>>>>>>>>>>>>> Extracted text >>>>>>>>>>>>>>>>>>")
                return text
            except Exception as e:
                return f"Error: Failed to fetch the webpage. {str(e)}"

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> str:
        """
        Delegates to the synchronous invoke method for now.
        """
        return self.invoke(args, sly_data)

    def request_content(self, url: str, headers: dict[str, str]) -> requests.Response:
        """
        Requests the content from a given URL with specified headers. If the first try fails, it retries once after a
        short delay.
        """
        try:
            response = requests.get(url, headers=headers, timeout=60)
            response.raise_for_status()
        # We try again if the request fails. If the second try doesn't work, just return the error message.
        except requests.RequestException as e:
            print("Failed to fetch webpage. Retrying in 10 seconds...")
            print(f"Error: {e}")
            time.sleep(10)
            try:
                response = requests.get(url, headers=headers, timeout=60)
                response.raise_for_status()
            except requests.RequestException as f:
                print(f"Retry failed: {f}")
                return None
        return response

    def read_html(self, url: str, headers: dict[str, str]) -> str:
        """
        Reads the content from a given URL that links to an HTML page.

        :param url: The URL of the webpage to read.
        :return: The text content of the webpage.
        """
        response = self.request_content(url, headers)
        if response is None:
            return "Error: Failed to fetch the webpage after retrying."

        soup = BeautifulSoup(response.text, "html.parser")
        texts = soup.stripped_strings
        full_text = " ".join(texts)
        return full_text

    def read_pdf(self, url: str, headers: dict[str, str]) -> str:
        """
        Reads the content from a given URL that links to a PDF file.

        :param url: The URL of the PDF file to read.
        :return: The text content of the PDF file.
        """
        response = self.request_content(url, headers)
        if response is None:
            return "Error: Failed to fetch the PDF after retrying."

        # Step 2: Load PDF into pypdf reader
        pdf_file = BytesIO(response.content)
        reader = PdfReader(pdf_file)

        # Step 3: Extract text from all pages
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""

        return text
