
from typing import Annotated, Dict

from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse

from auth_ops import generate_authorziation_code


# to-improve: secret should be hashed
client_id_secret_pairs = {
    "ex_client_id": "00000000"
}

# to-improve: password should be hashed
username_password_pairs = {
    "admin": "admin"
}

# to-complete: there is no expired time of authorization codes
# A dict with key as authorization code and client_id as value 
authorization_codes: Dict[str, str] = {}

# to-complete: scheme of generating access token is yet to implement 
# by auth_server and api_server
EXAMPLE_ACCESS_TOKEN = 'example_access_token'

app = FastAPI()


@app.get("/authorize", response_class=HTMLResponse)
async def query_user_to_authorize(
        response_type: str | None = None,
        client_id: str | None = None,
        redirect_url: str | None = None,   
):
    """
    Authorization page for user to provide credentials to
    authorize client to access resouce in api_server
    """
    
    html_template = \
"""
<html>
    <head>
        <title>Authorization</title>
    </head>
    <body>
        <div>
            <h2>auth_server</h2>
        </div>
        <div>
            <p><b>{client_id}</b> is requesting access to access api_server <mark>/example_resource</mark> endpint.</p>
            <p>Fill the required info below to sign in to get access to api_server</p>
            <form action="/authorize" method="post">
                <p>
                <label for="username">Username:</label></br>
                <input type="text" name="username" id="username">
                </p>
                <p>
                <label for="password">Password:</label></br>
                <input type="password" name="password" id="password">
                </p>
                <input type="hidden" name="client_id" value="{client_id}">
                <input type="hidden" name="redirect_url" value="{redirect_url}">
                <p>
                <input type="submit" value="Sign in">
                </p>
            </form>
        </div>
    </body>
</html>
"""

    if response_type != "code" or client_id is None \
        or redirect_url is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid request"
        )
    
    if client_id not in client_id_secret_pairs.keys():
        raise HTTPException(
            status_code=400,
            detail="client id cannot be found "
        )
    
    return html_template.format(
        client_id=client_id,
        redirect_url=redirect_url
    )


@app.post("/authorize", response_class=RedirectResponse)
async def issue_authorization_code(
        username: Annotated[str, Form()],
        password: Annotated[str, Form()],
        client_id: Annotated[str, Form()],
        redirect_url: Annotated[str, Form()]
):
    """
    Issue authorization code and redirect user to client_server callback 
    endpoint to acquire the access token if correct info is provided by 
    user.
    """

    if None in [username, password, client_id, redirect_url]:
        raise HTTPException(
            status_code=400,
            detail="Missing required parameters for authorization"
        )
    
    if client_id not in client_id_secret_pairs.keys():
        raise HTTPException(
            status_code=401,
            detail="Invalid client_id"
        )
    
    if username_password_pairs.get(username) == password:
        authorization_code = generate_authorziation_code(
            client_id,
            redirect_url
        )
        authorization_codes[authorization_code] = client_id
        print(f"{redirect_url}?code={authorization_code}")
        return RedirectResponse(
            url=f"{redirect_url}?code={authorization_code}",
            status_code=303
        )
    else:
        raise HTTPException(
            status_code=401,
            detail="Incorrect user credential"
        )
    

@app.post("/token")
async def issue_access_token(
    code: Annotated[str, Form()],
    grant_type: Annotated[str, Form()],
    redirect_url: Annotated[str, Form()],
    client_id: Annotated[str, Form()],
    client_secret: Annotated[str, Form()]
):
    """
    Issue access token to client if client provide the correct reqest info
    """

    if None in [code, grant_type, redirect_url, client_id, client_secret]:
        raise HTTPException(
            status_code=401,
            detail="Invalid client_id"
        )
    
    if grant_type != "code":
        raise HTTPException(
            status_code=400,
            detail="Invalid grant type"
        )
    
    if client_id_secret_pairs.get(client_id) == client_secret \
        and authorization_codes.get(code) == client_id:
        return {"access_token": EXAMPLE_ACCESS_TOKEN, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=401,
            detail="Invalid info provided"
        )

