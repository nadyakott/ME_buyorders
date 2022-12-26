from typing import List, Dict, Any
import aiohttp
from yarl import URL

from schemas.response import ItemResponseInfo, BidResponseInfo

from libs.logger import logger
from libs.session import Session
from libs.settings import settings

from client.magic_eden.bid.bid import BidInfo
from client.magic_eden.url_builder import UrlBuilder

class MagicEden(Session):

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0',
               'Host':'api-mainnet.magiceden.io',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
               'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
               'Accept-Encoding': 'gzip, deflate, br',
               'Referer': 'https://magiceden.io/',
               'Connection': 'keep-alive',
               'Upgrade-Insecure-Requests': '1',
               'Sec-Fetch-Dest': 'document',
               'Sec-Fetch-Mode': 'navigate',
               'Sec-Fetch-Site': 'same-origin',
               'Sec-Fetch-User': '?1',
               'TE': 'trailers',
               'Pragma': 'no-cache',
               'Cache-Control': 'no-cache'}

    def __init__(self):
        super(MagicEden, self).__init__()
        self.base_url = "https://api-mainnet.magiceden.io/"
        self.base_url_dev = "https://api-mainnet.magiceden.dev/"
        self.necessary_cookies = ()

    async def request(
            self,
            url: str,
            method: str = 'GET',
            **kwargs,
    ) -> aiohttp.ClientResponse:

        logger.info('request to {}'.format(url))

        logger.info(self.session.headers)
        logger.info(len(self.session.cookie_jar))

        try:
            response = await self.session.request(
                url=url,
                method=method,
                **kwargs,
            )
            logger(response)

            return await response
        except Exception as e:
            print(self.session)

    async def collect_lots(self, collectionSymbol: str, limit: int = 150, offset: int = 0) -> Dict[str, Any]:
        api = 'idxv2/getAllNftsByCollectionSymbol'
        params = {'collectionSymbol': collectionSymbol,
                  'onChainCollectionAddress': '',
                  'direction': 1,
                  'field': 1,
                  'limit': limit,
                  'offset': offset}

        url = UrlBuilder.get_url(self.base_url, api, params)
        response = await self.request(url=url)
        return await response.json()

    async def find_all_lots(self, collectionSymbol: str) -> List[ItemResponseInfo]:
        limit = 150
        offset = 0
        all_items = []
        result = await self.collect_lots(collectionSymbol)

        while result.get('results', False):
            all_items = all_items + [ItemResponseInfo(**item) for item in result.get('results')]
            offset += limit
            result = await self.collect_lots(collectionSymbol, limit=limit, offset=offset)
        return all_items

    async def get_bids_by_mint_addresses(self, mintAddresses: str) -> List[BidResponseInfo]:
        api = "idxv2/getBidsByMintAddresses"
        params = {'hideExpired': 'true',
                  'mintAddresses': mintAddresses,
                  'direction': 1,
                  'field': 1,
                  'limit': 500,
                  'offset': 0}

        url = UrlBuilder.get_url(self.base_url, api, params)

        result = await self.request(url)
        result = await result.json()

        return [BidResponseInfo(**item) for item in result.get('results')] if result.get('results', False) else []

    async def place_bid(self, bidInfo: BidInfo) -> aiohttp.ClientResponse:
        api = "v2/instructions/buy_change_price"
        params = {
            'buyer': bidInfo.buyer,
            'auctionHouseAddress': bidInfo.auctionHouseAddress,
            'tokenMint': bidInfo.tokenMint,
            'price': bidInfo.price,
            'newPrice': bidInfo.newPrice,
            'expiry': bidInfo.expiry}

        url = UrlBuilder.get_url(self.base_url_dev, api, params)

        result = await self.request(url)

        return result

    async def buy_and_deposit(self
                              , bidInfo: BidInfo
                              , headers: Dict[str, str] = {}) -> aiohttp.ClientResponse:
        api = "v2/instructions/buy_and_deposit"
        params = {
            'buyer': bidInfo.buyer,
            'auctionHouseAddress': bidInfo.auctionHouseAddress,
            'tokenMint': bidInfo.tokenMint,
            'price': bidInfo.price,
            'expiry': bidInfo.expiry,
            'useV2': 'false'}


        url = UrlBuilder.get_url(base_url=self.base_url
                                 , api_endpoint=api
                                 , params=params)

        result = await self.request(url, headers=headers)
        return result
