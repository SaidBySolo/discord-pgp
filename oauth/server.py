import os
from typing import Any
from sanic import Sanic, Request, response

from sanic.exceptions import BadRequest
from urllib.parse import urlencode
import aiohttp
from discord_pgp import database, pgp
from pgpy.constants import SignatureType

OAUTH2_CLIENT_ID = ""
OAUTH2_CLIENT_SECRET = ""
OAUTH2_REDIRECT_URI = ""

API_BASE_URL = os.environ.get("API_BASE_URL", "https://discordapp.com/api")
AUTHORIZATION_BASE_URL = API_BASE_URL + "/oauth2/authorize"
TOKEN_URL = API_BASE_URL + "/oauth2/token"

app = Sanic("server")
app.config["SECRET_KEY"] = OAUTH2_CLIENT_SECRET


async def exchange_code(code: str):
    data = {
        "client_id": OAUTH2_CLIENT_ID,
        "client_secret": OAUTH2_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": OAUTH2_REDIRECT_URI,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    async with aiohttp.ClientSession() as cs:
        async with cs.post(TOKEN_URL, data=data, headers=headers) as r:
            r.raise_for_status()
            return await r.json()


async def get_user_info(token: str):
    headers = {"Authorization": f"Bearer {token}"}

    async with aiohttp.ClientSession() as cs:
        async with cs.get(API_BASE_URL + "/users/@me", headers=headers) as r:
            r.raise_for_status()
            return await r.json()


@app.route("/")
async def index(request: Request):
    param: dict[str, Any] = {
        "client_id": OAUTH2_CLIENT_ID,
        "scope": " ".join(["identify", "email"]),
        "response_type": "code",
        "redirect_uri": OAUTH2_REDIRECT_URI,
    }
    return response.redirect(f"{API_BASE_URL}/oauth2/authorize?{urlencode(param)}")


@app.route("/callback")
async def callback(request: Request):
    code = request.args.get("code")
    if not code:
        raise BadRequest
    access_token_res = await exchange_code(code)
    token = access_token_res["access_token"]
    user_info = await get_user_info(token)
    users = database.read()

    email = user_info["email"]

    for user in users:
        if user["user_id"] == int(user_info["id"]):
            key = pgp.get_key(user["key"])

            infos, _ = pgp.get_info(key)
            for info in infos:
                if info.email == email:
                    if info.sig is not SignatureType.Positive_Cert:
                        return response.text("그... 맞긴한데... 제대로된거 가져오셈")
                    user["verified"] = True
                    database.write(users)
                    return response.text("등록했다")
            else:
                return response.text("있는게 없다.")

    return response.text("키먼저 등록하고 오셈")
