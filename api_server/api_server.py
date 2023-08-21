from typing import Annotated, Union

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer


EXAMPLE_ACCESS_TOKEN = 'example_access_token'

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8001/token")

app = FastAPI()


@app.get("/example_resource")
async def example_reource(
    access_token: Annotated[Union[str, None], Depends(oauth2_scheme)] = None
):
    if access_token and access_token == EXAMPLE_ACCESS_TOKEN:
        return {"data": "example reource ABCD"}
    else:
        raise HTTPException(
            status_code=401,
            detail="Missing required parameters for authorization"
        )
