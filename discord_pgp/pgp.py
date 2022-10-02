# type: ignore
from typing import IO, Union
from pgpy import PGPKey, PGPUID
from discord_pgp.domain.info import Info

def get_info(blob: Union[str, bytes, bytearray]):
    infos: list[Info] = []
    pub_key, _ = PGPKey.from_blob(blob)

    pub_key: PGPKey
    userid: PGPUID
    for userid in pub_key.userids:
        info = Info(userid.email, userid.name, userid.__sig__[-1].type)
        infos.append(info)
    return infos, pub_key.key_algorithm.name
