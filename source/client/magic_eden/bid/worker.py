from typing import List, Tuple
from source.client.magic_eden.endpoints import MagicEden
from source.schemas.response import BidResponseInfo
from source.libs.settings import settings
from source.client.magic_eden.bid.bid import BidInfo
import datetime


class Worker:

    def __init__(self
                 , magic_eden_client: MagicEden
                 , min_price: float
                 , max_price: float
                 , mintAccAddress: str
                 ):
        self.magic = magic_eden_client
        self.MIN_DELTA_PRICE = settings.MIN_DELTA_PRICE
        self.LAMPORT_RATE = settings.LAMPORT_RATE
        self.MIN_PRICE = min_price
        self.MAX_PRICE = max_price
        self.bids: List[BidResponseInfo]
        self.mintAccAddress = mintAccAddress
        self.expiry = datetime.datetime.timestamp(datetime.datetime.now()) + settings.ADD_TIME
        self.tokenMint = settings.TOKEN_MINT


    async def get_bids(self) -> List[BidResponseInfo]:
        self.bids = await self.magic.get_bids_by_mint_addresses(self.mintAccAddress)
        return self.bids

    def get_new_price_bid(self) -> BidInfo:
        our_bid_price = 0
        for bid in self.bids:
            if bid.is_first_bid_not_our():
                if bid.is_bid_price_in_boundaries(self.MIN_PRICE, self.MAX_PRICE):
                    new_price = bid.update_price(bid.bidderAmountLamports)

                    return BidInfo(settings.BIDDER_PUBKEY
                                   , bid.v2.auctionHouseKey
                                   , self.tokenMint
                                   , bid.bidderAmountLamports
                                   , new_price
                                   , self.expiry)
            else:
                our_bid_price = bid.bidderAmountLamports

        new_price = settings.MIN_DELTA_PRICE + self.MIN_PRICE
        return BidInfo(settings.BIDDER_PUBKEY
                                   , settings.AUCTION_HOUSE_ADDRESS
                                   , self.tokenMint
                                   , our_bid_price
                                   , new_price
                                   , self.expiry)
