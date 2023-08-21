import hashlib


def generate_authorziation_code(client_id, redirect_url):
    """
    Generate authorization code based on client_id and 
    redirect_url.
    
    This function can be improved with more sophisticate 
    algorithm to generate the authorization code with 
    the client_id and redirect_url .
    """
    code = hashlib.sha256(
        f"{client_id}{redirect_url}".encode()
    ).hexdigest()

    return code