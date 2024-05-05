def twocap_endpoint(
    client, sitekey, captcha_token, page_action, user_agent, ip_address
):
    """
    Send a POST request to the 2captcha endpoint with the provided data and return the updated JSON response.

    Args:
        client: The HTTP client used to make the POST request.
        sitekey: The site key for the captcha.
        captcha_token: The token generated for the captcha.
        page_action: The action associated with the page.
        user_agent: The user agent string.
        ip_address: The IP address used for the request.

    Returns:
        dict: The updated JSON response including additional data like action, user_agent, and ip_address.
    """

    response = client.post(
        "https://2captcha.com/api/v1/captcha-demo/recaptcha-enterprise/verify",
        headers={"Content-Type": "application/json"},
        json={
            "siteKey": sitekey,
            "token": captcha_token,
        },
    )
    response_json = response.json()
    response_json.update(
        {"action": page_action, "user_agent": user_agent, "ip_address": ip_address}
    )
    return response_json
