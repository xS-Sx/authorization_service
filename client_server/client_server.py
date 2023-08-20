from typing import Annotated, Union
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import HTMLResponse, RedirectResponse
import requests

AUTH_ENDPOINT = "http://localhost:8001/authorize"
TOKEN_ENDPOINT = "http://localhost:8001/token"
RES_ENDPOINT = "http://localhost:8002/example_resource"
REDIRECT_URL = "http://localhost:8000/auth_cb"


CLIENT_ID = "ex_client_id"
CLIENT_SECRET = "00000000"

app = FastAPI()

example_api_access_token = None


@app.get("/login", response_class=HTMLResponse)
async def get_authorization_token():
    """
    Return a link to connect to auth_server to acquire the authorization code
    """

    html_template = \
"""
<html>
    <head>
        <title>Sign in</title>
    </head>
    <body>
        <div>
            <h2>client_server</h2>
        </div>
        <div>
            <p>
                <a href="{auth_endpoint}?response_type=code&client_id={client_id}&redirect_url={redirect_url}">click here
                </a>
                to sign in via authorization server to access api resource
            </p>
        </div>
    </body>
</html>
"""
    
    return html_template.format(
        auth_endpoint=AUTH_ENDPOINT,
        client_id=CLIENT_ID,
        redirect_url=REDIRECT_URL
    )


@app.get("/auth_cb")
async def get_access_token(code: str | None = None):
    """
    Callback endpoint for auth_server to redirect for access token acquirement. 
    Redirect user to /example_resource endpoint if access token is acquired successfully.

    Param:
        code (str|None): authorization code from from query string
    
        Returns:
            (RedirectResponse|HTTPException): HTTP Response.

    """
    global example_api_access_token

    if code is not None:
        try:
            resp = requests.post(    
                TOKEN_ENDPOINT,
                data = {
                    "code": code,
                    "grant_type": "code",
                    "redirect_url": REDIRECT_URL,
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET
                }
            )

            if resp.status_code == 200:
                example_api_access_token = resp.json().get("access_token")
                return RedirectResponse(app.url_path_for("read_api_resource"))
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Fail to acquire access from auth_server"
                )
        except:
            raise HTTPException(
                status_code=500,
                detail="Fail to get response from auth_server"
            )


@app.get("/example_resource")
async def read_api_resource():
    """
    Return api resource from api_server if client is authorized with access token.
    If client is not authorzied, user is redirect to sign in to acquire access token for client.
    """

    if example_api_access_token is not None:
        try:
            resp = requests.get(RES_ENDPOINT, headers = {
                "Authorization": f"Bearer {example_api_access_token}"
            })
            if resp.status_code == 200:
                return resp.json()
            else:
                raise HTTPException(
                    status_code=resp.status_code,
                    detail="Fail to retrive api resource"
                )
        except:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Fail to retrive api resource. " "api_server may be down"
                )
            )
    else:
        return RedirectResponse(app.url_path_for("get_authorization_token"))

        

