from typing import List, Optional
from pydantic import BaseModel

from schemas.config import Trait, RankInfo
from libs.config import settings

# from source.schemas.config import Trait, RankInfo
# from source.libs.config import settings

class RarityInfo(BaseModel):
    merarity: Optional[RankInfo]

class ItemResponseInfo(BaseModel):
    mintAddress: Optional[str]
    title: Optional[str]
    price: Optional[float]
    attributes: Optional[List[Trait]]
    rarity: Optional[RarityInfo]

class AuctionBidResponseInfo(BaseModel):
    auctionHouseKey: Optional[str]
    buyerReferral: Optional[str]

class BidResponseInfo(BaseModel):

    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    #     self.buyerPubKey = kwargs['buyerPubKey']

    v2: Optional[AuctionBidResponseInfo]
    bidderPubkey: Optional[str]
    bidderAmountLamports: Optional[float]

    def convert_price(self) -> float:
        return self.bidderAmountLamports / settings.LAMPORT_RATE

    def is_first_bid_not_our(self) -> bool:
        if self.bidderPubkey != settings.BIDDER_PUBKEY:
            return True
        return False

    # def is_bid_price_in_boundaries(self, converted_price:float, min_price: float, max_price: float) -> bool:
    #     if converted_price >= min_price and converted_price < max_price:
    #         return True
    #     return False

    def is_bid_price_in_boundaries(self, min_price: float, max_price: float) -> bool:
        if self.bidderAmountLamports >= min_price * settings.LAMPORT_RATE and self.bidderAmountLamports < max_price * settings.LAMPORT_RATE - settings.MIN_DELTA_PRICE:
            return True
        return False

    def update_price(self, current_price: float) -> float:
        return current_price + settings.MIN_DELTA_PRICE





