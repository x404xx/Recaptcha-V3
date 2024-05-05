from endpoints import ant_endpoint, twocap_endpoint
from src import CaptchaSolver, HttpClient, RichConsole

# * PROXY URL examples
# "http://username:password@host:port"
# "socks5://username:password@host:port"

VERBOSE = True
LOG_HANDLER = True
PROXY_URL = None

ANT_URL = "https://antcpt.com/score_detector/"
TWO_URL = "https://2captcha.com/demo/recaptcha-v3-enterprise"


def get_ip(client):
    """
    Retrieves the public IP address using the provided HTTP client.

    Args:
        client: The HTTP client used to make the request.

    Returns:
        str: The public IP address extracted from the JSON response.
    """
    response = client.get("https://jsonip.com/")
    return response.json()["ip"]


# TODO: Implement this section below based on the website that needs to be bypassed.
def solve_v3(is_ant=False, is_two=False):
    BASE_URL = ANT_URL if is_ant else TWO_URL if is_two else None

    if BASE_URL is None:
        raise ValueError("Either 'is_ant' or 'is_two' must be True")

    solver = CaptchaSolver(BASE_URL, VERBOSE)

    with HttpClient(PROXY_URL, LOG_HANDLER) as client:
        ip_address = get_ip(client)
        user_agent = client.base_agent["User-Agent"]
        captcha_token = solver.solve_captcha(client)
        page_action = solver.page_action

        if is_two:
            sitekey = solver.sitekey
            return twocap_endpoint(
                client, sitekey, captcha_token, page_action, user_agent, ip_address
            )
        elif is_ant:
            return ant_endpoint(
                client, captcha_token, page_action, user_agent, ip_address
            )


if __name__ == "__main__":
    RichConsole.clear()
    RichConsole.print(solve_v3(is_ant=True))
