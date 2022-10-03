import json
from typing import Any

path = "database.json"


def read():
    with open(path, "r", encoding="UTF-8") as f:
        return json.loads(f.read())


def write(o: list[dict[str, Any]]):
    dumped = json.dumps(o)
    with open(path, "w", encoding="UTF-8") as f:
        f.write(dumped)


def add_user(info: dict[str, Any]):
    data = read()
    data.append(info)
    write(data)

