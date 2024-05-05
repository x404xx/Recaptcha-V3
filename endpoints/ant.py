def ant_endpoint(client, captcha_token, page_action, user_agent, ip_address):
    """
    Send a POST request to an endpoint with a captcha token and additional information.

    Args:
        client: The HTTP client used to make the POST request.
        captcha_token (str): The captcha token to be sent in the request.
        page_action (str): The action related to the page.
        user_agent (str): The user agent string.
        ip_address (str): The IP address of the client.

    Returns:
        dict: A dictionary containing the response JSON merged with additional information.
    """
    response = client.post(
        "https://antcpt.com/score_detector/verify.php",
        headers={"Content-Type": "application/json"},
        json={"g-recaptcha-response": captcha_token},
    )
    response_json = response.json()
    response_json.update(
        {"action": page_action, "user_agent": user_agent, "ip_address": ip_address}
    )
    return response_json
