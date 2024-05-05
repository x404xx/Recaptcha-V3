import base64
import re
from dataclasses import dataclass
from urllib.parse import urlparse

from rich.box import HEAVY
from rich.table import Table
from rich.traceback import install as traceback_install

from .rich_console import RichConsole

traceback_install(show_locals=True, word_wrap=True)


@dataclass
class CaptchaData:
    """
    Represents the data structure for captcha-related information.

    Args:
        sitekey: The sitekey used in the captcha challenge.
        page_action: The action related to the captcha challenge.
        api_type: The type of API used in the captcha challenge.
        constructed_url: The URL constructed for the captcha challenge.
        co_value: The value encoded for the captcha challenge.
        anchor_url: The URL of the anchor used in the captcha challenge.
        anchor_token: The token associated with the anchor in the captcha challenge.
        captcha_token: The token generated after solving the captcha challenge.
    """

    sitekey: str
    page_action: str
    api_type: str
    constructed_url: str
    co_value: str
    anchor_url: str
    anchor_token: str
    captcha_token: str


class CaptchaSolver:
    """
    Initializes the captcha solver with the base URL and verbosity option.

    Args:
        base_url (str): The base URL for the captcha solver.
        verbose (bool, optional): Whether to print Captcha data information. Defaults to false.

    Methods:
        - extract_data: Extracts data from a URL response based on a given pattern.
        - get_sitekey: Gets the sitekey from the response text.
        - get_page_action: Extracts the action value from the page content.
        - construct_url: Constructs a URL with a specified port based on the base URL.
        - encode_co: Encodes the constructed URL.
        - get_api_type: Get the API type.
        - construct_anchor: Construct the anchor URL for a Google reCAPTCHA.
        - get_anchor_token: Get the anchor token from the provided anchor URL.
        - build_payload: Build a payload string for a CAPTCHA request.
        - get_captcha_token: Get the CAPTCHA token for a given CAPTCHA challenge.
        - solve_captcha: Solves a captcha challenge and returns the captcha token.

    Raises:
        ValueError: If sitekey is not found.
    """

    CAPTCHA_URL = "https://www.google.com/recaptcha"

    def __init__(self, base_url, verbose=False):
        """
        Initializes the captcha solver with the base URL and verbosity option.

        Args:
            base_url (str): The base URL for the captcha solver.
            verbose (bool, optional): Whether to print Captcha data information. Defaults to false.
        """
        self._base_url = base_url
        self._verbose = verbose
        self.sitekey = None
        self.page_action = None

    def _extract_data(self, client, url, pattern):
        """
        Extracts data from a URL response based on a given pattern.

        Args:
            client: The HTTP client used to make the request.
            url (str): The URL to fetch the data from.
            pattern (str): The regex pattern to search for in the response.

        Returns:
            str or None: The extracted data if found, otherwise None.
        """
        response = client.get(url)
        if match := re.search(pattern, response.text):
            return match[1] or match[2] or match[3] or None
        return None

    def _get_sitekey(self, client):
        """
        Gets the sitekey from the response text.

        Args:
            client: The HTTP client used to make the request.

        Returns:
            str or None: The sitekey extracted from the response text, or None if not found.
        """
        pattern = r"render=(.*?)'|execute\('(.*?)'|&#x27;(.*?)&"
        return self._extract_data(client, self._base_url, pattern)

    def _get_page_action(self, client):
        """
        Extracts the action value from the page content.

        Args:
            client: The HTTP client used to make the request.

        Returns:
            str: The action value extracted from the page content.
        """
        pattern = r"action: '(.*?)'"
        return self._extract_data(client, self._base_url, pattern)

    def _construct_url(self, port="443"):
        """
        Constructs a URL with a specified port based on the base URL.

        Args:
            port (str): The port number to append to the URL. Defaults to "443".

        Returns:
            str: The constructed URL with the specified port.
        """
        parsed_url = urlparse(self._base_url)
        return f"{parsed_url.scheme}://{parsed_url.netloc}:{port}"

    def _encode_co(self, constructed_url):
        """
        Encodes the constructed URL.

        Args:
            constructed_url (str): The URL to be encoded.

        Returns:
            str: The encoded URL.
        """
        encoded_url = base64.b64encode(constructed_url.encode()).decode()
        return encoded_url.rstrip("=") + "." * (
            len(encoded_url) - len(encoded_url.rstrip("="))
        )

    def _get_api_type(self, client):
        """
        Get the API type.

        Args:
            client: The HTTP client used to make the request.

        Returns:
            str or None: The API type extracted from the response text, or None if not found.
        """
        pattern = r"/recaptcha/(api|enterprise)\."
        api_type = self._extract_data(client, self._base_url, pattern)
        return "api2" if api_type == "api" else "enterprise"

    def _construct_anchor(self, sitekey, co_value, api_type):
        """
        Construct the anchor URL for a Google reCAPTCHA.

        Args:
            sitekey (str): The sitekey for the reCAPTCHA.
            co_value (str): The value of the 'co' parameter.
            api_type (str): The type of reCAPTCHA API.

        Returns:
            str: The constructed anchor URL for the reCAPTCHA.
        """
        return f"{self.CAPTCHA_URL}/{api_type}/anchor?ar=1&k={sitekey}&co={co_value}&hl=en&size=invisible"

    def _get_anchor_token(self, client, anchor_url):
        """
        Get the anchor token from the provided anchor URL.

        Args:
            client: The HTTP client used to make the request.
            anchor_url (str): The URL to fetch the anchor token from.

        Returns:
            str or None: The anchor token extracted from the response text, or None if not found.
        """
        pattern = r'recaptcha-token" value="(.*?)"'
        return self._extract_data(client, anchor_url, pattern)

    def _build_payload(self, anchor_token, co_value, sitekey):
        """
        Build a payload string for a CAPTCHA request.

        Args:
            anchor_token (str): The anchor token for the CAPTCHA request.
            co_value (str): The co value for the CAPTCHA request.
            sitekey (str): The sitekey for the CAPTCHA request.

        Returns:
            str: A formatted payload string for the CAPTCHA request.
        """
        return f"reason=q&c={anchor_token}&k={sitekey}&co={co_value}"

    def _get_captcha_token(self, client, anchor_token, co_value, sitekey, api_type):
        """
        Get the CAPTCHA token for a given CAPTCHA challenge.

        Args:
            client: The HTTP client used to make the request.
            anchor_token (str): The anchor token for the CAPTCHA request.
            co_value (str): The co value for the CAPTCHA request.
            sitekey (str): The sitekey for the CAPTCHA request.
            api_type (str): The type of reCAPTCHA API to use.

        Returns:
            str: The CAPTCHA token extracted from the response, or None if not found.
        """
        response = client.post(
            f"{self.CAPTCHA_URL}/{api_type}/reload",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            params={"k": sitekey},
            data=self._build_payload(anchor_token, co_value, sitekey),
        )
        match = re.search(r'"rresp","(.*?)"', response.text)
        return match[1] if match else None

    def solve_captcha(self, client):
        """
        Solves a captcha challenge using the provided client.

        Args:
            client: The HTTP client used to make the request.

        Returns:
            str: The captcha token generated after solving the captcha challenge.

        Raises:
            ValueError: If the sitekey is not found.
        """
        self.sitekey = self._get_sitekey(client)
        if not self.sitekey:
            raise ValueError("Sitekey not found!")
        self.page_action = self._get_page_action(client)
        api_type = self._get_api_type(client)
        if not api_type:
            raise ValueError(
                f"API Type not found! Please check the response text from {self._base_url}"
            )
        constructed_url = self._construct_url()
        co_value = self._encode_co(constructed_url)
        anchor_url = self._construct_anchor(self.sitekey, co_value, api_type)
        anchor_token = self._get_anchor_token(client, anchor_url)
        captcha_token = self._get_captcha_token(
            client, anchor_token, co_value, self.sitekey, api_type
        )

        if self._verbose:
            captcha_data = CaptchaData(
                sitekey=self.sitekey,
                page_action=self.page_action,
                api_type=api_type,
                constructed_url=constructed_url,
                co_value=co_value,
                anchor_url=anchor_url,
                anchor_token=anchor_token,
                captcha_token=captcha_token,
            )
            table = Table(show_header=False, box=HEAVY, border_style="purple")
            table.add_column("Field", style="medium_purple")
            table.add_column("Value", style="dodger_blue2")
            for field, value in captcha_data.__dict__.items():
                table.add_row(field, value)

            RichConsole.print(table)

        return captcha_token
