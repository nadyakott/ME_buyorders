import csv
from typing import Dict, Any, List, Optional

from libs.settings import settings
from schemas.config import Item, Trait

class ConfigItemsParser:

    def __init__(self):
        self.FILE_PATH: str = settings.FILE_PATH
        self.ITEMS = self.read_config_items()

    def read_config_items(self) -> List[Item]:
        with open(self.FILE_PATH, newline='') as f:
            reader = csv.DictReader(f)
            temp = list()
            for item in reader:
                temp.append(Item(MODULE=item.get('MODULE'),
                     WALLET_ALIAS=item.get('WALLET_ALIAS'),
                     COLLECTION_NAME=item.get('COLLECTION_NAME'),
                     MAX_PRICE=self.convert_buy_price_to_float(item.get('MAX_PRICE')),
                     MIN_PRICE=self.convert_buy_price_to_float(item.get('MIN_PRICE')),
                     MAX_AMOUNT=float(item.get('MAX_AMOUNT')),
                     TRAITS=self.split_traits(item.get('TRAITS')),
                     MAX_RANK=self.convert_max_rank_to_int(item.get('MAX_RANK')),
                     TX_PER_SNIPE=item.get('TX_PER_SNIPE'),
                     PROXIES=item.get('PROXIES'),
                     MODE=item.get('MODE'),
                     EXTRA_FEE=item.get('EXTRA_FEE')))
            return temp

    def convert_max_rank_to_int(self, max_rank: str) -> int:
        return int(max_rank) if max_rank else -1

    def convert_buy_price_to_float(self, price: str) -> float:
        return float(price) if price else 0

    def split_traits(self, traits: str) -> Optional[List[Trait]]:
        if traits:
            conditions = traits.split(sep='|')
            parsed_traits = [trait.split(':::') for trait in conditions]
            return [Trait(trait_type=trait[0], value=trait[1]) for trait in parsed_traits]
        return None

config = ConfigItemsParser()
