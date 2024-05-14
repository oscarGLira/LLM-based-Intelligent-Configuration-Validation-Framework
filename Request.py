import requests
import os
import pandas as pd
import ollama
import time
from datetime import timedelta

# Replace the IP address and port with the appropriate values
BATFISH_IP = 'batfish_ip' # # change batfish_ip to the batfish docker ip
BATFISH_IP_PORT = '5000' # batfish application port (defualt: 5000)
MODEL_NAME = 'zephyr_configurator' # model to be used on the LLM module (defualt: zephyr_configurator)

def request_status():
    try:
        # Make a GET request to the /topology route
        response = requests.get(f"http://{BATFISH_IP}:{BATFISH_IP_PORT}/topology")

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Print the response content (topology information)
            return response.json()
        else:
            return ("Failed to retrieve topology information. Status code:", response.status_code)
    except Exception as e:
        return ("An error occurred:", str(e))

def send_verification_request(verification_type, config_commands):
    url = f"http://{BATFISH_IP}:{BATFISH_IP_PORT}/verify"
    payload = {
        "verification_type": verification_type,
        "commands": config_commands
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

if __name__ == "__main__":
    # Read the content of the prompts files
    translation_path = 'translator.txt'
    configuration_path = 'configurator.txt'

    with open(translation_path, "r") as file:
        translator = file.read().strip()

    with open(configuration_path, "r") as file:
        configurator = file.read().strip()

    # Check if variables are empty and stop the program if they are
    if not translator:
        raise ValueError("Translator file is empty. Program stopped.")

    if not configurator:
        raise ValueError("Configurator file is empty. Program stopped.")

    # If variables are not empty, continue with the program

    while True:
        requirement = input('Network Requirement: ')

        # Craft the prompt with actual network status
        topology_status = request_status()  # Batfish communication must be established
	
        print("""
            \n------------------------ Topology Status ----------------------------\n
        """)
        print(topology_status)
	
        translator_prompt = translator + str(
            topology_status) + "\n Use this information to gather relevant network information for the {requirements} goal. You are not authorized to make explanations of any type."

        # Call llm_translation or llm_config based on your requirement
        trad = ollama.chat(model=MODEL_NAME,
                           messages=[{'role': 'system', 'content': translator_prompt}, {'role': 'user', 'content': requirement}])

        print("""
            \n------------------------ Translation Model Answer ----------------------------\n
        """)
        print(trad)

        trad_response = trad['message']['content']

        # Identify the configuration verification type based on the first two characters of trad_response
        verification_type = trad_response[:2]

        if trad:
            config = ollama.chat(model=MODEL_NAME,
                                 messages=[{'role': 'system', 'content': configurator}, {'role': 'user', 'content': trad_response}])
            if config:
                print("""
                    \n------------------------ Configuration Model Answer ----------------------------\n
                """)
                print(config)
                config_response = config['message']['content']

                # Send config_response to Batfish for verification
                verification_result = send_verification_request(verification_type, config_response)
                print("Verification result for", verification_type, ":", verification_result)
            else:
                print("Configuration failed for requirement:", requirement)
        else:
            print("Translation failed for requirement:", requirement)
