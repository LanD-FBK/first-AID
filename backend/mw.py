from datetime import timedelta

import jwt
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from routes.login import create_access_token
from sql.dboptions import getOption


# https://stackoverflow.com/questions/71525132/how-to-write-a-custom-fastapi-middleware-class

class MyMiddleware(BaseHTTPMiddleware):
    def __init__(
            self,
            app,
    ):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):

        access_token = None
        if "authorization" in request.headers:
            token = request.headers['authorization'].replace("Bearer ", "")
            secret_key = getOption("SECRET_KEY")
            try:
                payload = jwt.decode(token, secret_key, algorithms=[getOption("JWT_ALGORITHM")])
                access_token_expires = timedelta(minutes=getOption("ACCESS_TOKEN_EXPIRE_MINUTES", ret_type=int))
                access_token = create_access_token(
                    data={"sub": payload['sub']}, expires_delta=access_token_expires
                )
            except:
                # TODO jwt.exceptions.DecodeError: Not enough segments
                pass

        # process the request and get the response
        response = await call_next(request)

        if access_token:
            response.headers["bearer-refreshed"] = access_token
            response.headers["access-control-expose-headers"] = "bearer-refreshed"

        return response
