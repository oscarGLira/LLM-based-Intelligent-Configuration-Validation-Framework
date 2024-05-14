from flask import Flask, request, jsonify
from pybatfish.client.session import Session
from pybatfish.question import bfq
from pybatfish.datamodel.flow import PathConstraints

app = Flask(__name__)

# Define Batfish session globally
bf = Session(host='batfish_ip') # change batfish_ip to the batfish docker ip
# Define snapshot name globally
snapshot_name = "snapshot-verify"

def snapshot_init():
    try:
        # Assign a friendly name to your network and snapshot
        NETWORK_NAME = "network-test-4routers"
        SNAPSHOT_NAME = "snapshot" # Specify the snapshot name

        # Specify the path to the snapshot directory
        snapshot_path = ".../snapshot"  # Replace with the actual path to your snapshot

        # Set the snapshot within the Batfish session
        bf.set_network(NETWORK_NAME)
        bf.init_snapshot(snapshot_path, name=SNAPSHOT_NAME, overwrite=True)  # Initialize with an empty config

        # Print a message when the snapshot is loaded
        print("Snapshot loaded")
    except Exception as e:
        print(f"Error during snapshot initialization: {str(e)}")


@app.route('/verify', methods=['POST'])
def verify_configuration():
    global snapshot_name  # Declare snapshot_name as global

    data = request.get_json()

    # Extract the verification details from the request
    verification_type = data.get("verification_type", "DEFAULT")
    commands = data.get("commands", [])
    identifier = data.get("identifier", "DEFAULT")  # Default identifier if not provided

    # Apply the received configuration to Batfish (if applicable)
    try:
        if verification_type == "APPLY_CONFIG":
            hostname = data.get("hostname", "")
            # Use bf_init_snapshot to set configuration
            bf.init_snapshot(name=snapshot_name, overwrite=True)
    except Exception as e:
        return jsonify({"result": "Error", "error": str(e)})

    # Proceed with the selected verification
    try:
        # Determine the type of Batfish question based on the identifier
        if identifier == "CP":
            # Configuration Properties question
            # Example: Get all interface names and descriptions
            result = bfq.interfaceProperties().answer()
        elif identifier == "TP":
            # Topology question
            # Example: Get layer 3 topology
            result = bfq.layer3Topology().answer()
        # Add more verification types as needed
        else:
            # Default to reachability check
            result = bfq.reachability(
                pathConstraints=PathConstraints(startLocation="enter(h1)", endLocation="enter(h2)")
            ).answer()

        # Process the verification result
        if result.frame().empty:
            return jsonify({"result": "Successful"})
        else:
            return jsonify({"result": "Verification failed", "details": result.frame().to_dict()})
    except Exception as e:
        # Print the specific error message
        print(f"Error during verification: {str(e)}")
        return jsonify({"result": "Error during verification", "error": str(e)})


@app.route('/syntax', methods=['POST'])
def syntax_checker_route():
    data = request.get_json()

    # Extract the configuration commands from the request
    commands = data.get("commands", [])

    # Perform syntax check
    syntax_check_result = syntax_checker(commands)
    return jsonify(syntax_check_result)


@app.route('/llm_response', methods=['POST'])
def apply_llm_response():
    data = request.get_json()

    # Extract the LLM response details from the request
    device_name = data.get("device_name", "")
    llm_response = data.get("llm_response", [])

    try:
        # Apply the received LLM response to Batfish
        apply_config_to_device("/home/user/MV_framework/snapshot", device_name, "\n".join(llm_response))
        return jsonify({"result": "Successful"})
    except Exception as e:
        return jsonify({"result": "Error during LLM response application", "error": str(e)})


def apply_config_to_device(snapshot_path, device_name, llm_response):
    existing_config = read_snapshot_config(snapshot_path, device_name)
    new_config = update_existing_config(existing_config, generate_cisco_config(llm_response, device_name))

    # Use bf_init_snapshot to set configuration
    bf.init_snapshot(input_text=new_config, name=snapshot_name, overwrite=True)


@app.route('/topology', methods=['GET'])
def get_topology():
    try:
        # Get the answer for the layer 3 edges question
        topology = bf.q.layer3Edges().answer().frame().to_json()
        return jsonify({"topology": topology})
    except Exception as e:
        return jsonify({"error": str(e)})


def read_config_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()


if __name__ == '__main__':
    snapshot_init()
    app.run(host='0.0.0.0', port=5000) # Anounce the application on every IP or change batfish_ip to the batfish docker ip
