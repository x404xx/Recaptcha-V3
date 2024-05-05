from random import uniform

import httpx
from user_agent import generate_user_agent as user_agent

from .rich_console import RichConsole


class LogHandler:
    """
    A class for logging HTTP requests and responses.

    Methods:
    - log_request: Logs the details of an HTTP request.
    - log_response: Logs the details of an HTTP response.

    Args:
    - request: The HTTP request object to log in the format "<Request> {method} {url} - Waiting for response".
    - response: The HTTP response object to log in the format "<Response> {status_code}".

    Returns:
    - None
    """

    @staticmethod
    def log_request(request):
        RichConsole.print(
            f"<Request> {request.method} {request.url} - Waiting for response"
        )

    @staticmethod
    def log_response(response):
        RichConsole.print(f"<Response> {response.status_code}", end="\n\n")


class HttpClient(LogHandler):
    """
    HttpClient class for making HTTP requests.

    Methods:
        __init__: Initialize the client with an optional proxy URL.
        __enter__: Enter method for context management.
        __exit__: Exit method for context management.
        _make_request: Make an HTTP request with error handling.
        get: Make a GET request to the specified URL.
        post: Make a POST request to the specified URL.

    Returns:
        None
    """

    def __init__(self, proxy_url=None, log_handler=False, timeout=uniform(10, 15)):
        """
        Initialize the client with an optional proxy URL.

        Args:
            proxy_url (str, optional): The proxy URL to use. Defaults to None.
            log_handler (bool, optional): Whether to print a log message. Defaults to False.
            timeout (float): A random timeout between 10 and 15 seconds will be used.

        Returns:
            None
        """
        self.base_agent = {"User-Agent": str(user_agent())}
        self._client = httpx.Client(
            headers=self.base_agent,
            proxy=proxy_url,
            timeout=timeout,
            event_hooks=(
                {
                    "request": [self.log_request],
                    "response": [self.log_response],
                }
                if log_handler
                else None
            ),
        )

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self._client.close()

    def _make_request(self, method, url, **kwargs):
        try:
            response = self._client.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except (httpx.HTTPError, Exception) as exc:
            raise exc

    def get(self, url, **kwargs):
        return self._make_request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self._make_request("POST", url, **kwargs)
