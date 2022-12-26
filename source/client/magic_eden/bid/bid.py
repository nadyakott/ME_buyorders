import datetime

class BidInfo:

    def __init__(self, buyer: str
                 , auctionHouseAddress: str
                 , tokenMint: str
                 , price: float
                 , newPrice: float
                 , expiry: datetime):

        self.buyer = buyer
        self.auctionHouseAddress = auctionHouseAddress
        self.tokenMint = tokenMint
        self.price = price
        self.newPrice = newPrice
        self.expiry =  expiry





