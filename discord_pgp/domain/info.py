from dataclasses import dataclass
from pgpy.constants import SignatureType

@dataclass
class Info:
    email : str
    name: str
    sig: SignatureType