# type: ignore
from typing import IO, Union
from pgpy import PGPKey, PGPUID
from discord_pgp.domain.info import Info


def get_info(key: PGPKey) -> tuple[list[Info], str]:
    infos: list[Info] = []

    userid: PGPUID
    for userid in key.userids:
        info = Info(userid.email, userid.name, userid.__sig__[-1].type)
        infos.append(info)
    return infos, key.key_algorithm.name


def get_key(blob: Union[str, bytes, bytearray]) -> PGPKey:
    pub_key, _ = PGPKey.from_blob(blob)
    return pub_key
