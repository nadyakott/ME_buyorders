from typing import Optional, List
from pydantic import BaseModel


class RankInfo(BaseModel):
    rank: Optional[int]

class Trait(BaseModel):
    trait_type: Optional[str]
    value: Optional[str]

    def __eq__(self, other):
        if not isinstance(other, Trait):
            return NotImplemented
        return self.trait_type.lower() == other.trait_type.lower() and self.value.lower() == other.value.lower()

class Item(BaseModel):

    MODULE: Optional[str]
    WALLET_ALIAS: Optional[str]
    COLLECTION_NAME: Optional[str]
    MAX_PRICE: Optional[float]
    MIN_PRICE: Optional[float]
    MAX_AMOUNT: Optional[str]
    TRAITS: Optional[List[Trait]]
    MAX_RANK: Optional[int]
    TX_PER_SNIPE: Optional[str]
    PROXIES: Optional[str]
    MODE: Optional[str]
    EXTRA_FEE:Optional[str]
