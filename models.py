import base64

def encode_base64(data):
    return base64.b64encode(data.encode()).decode()

def decode_base64(data):
    # Ensure the data has correct padding
    padding = len(data) % 4
    if padding != 0:
        data += '=' * (4 - padding)  # Add the required padding

    return base64.b64decode(data.encode()).decode()

