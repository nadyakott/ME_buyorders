from source.libs.logger import logger
from schemas.response import ItemResponseInfo
from schemas.config import Trait
from typing import Optional, List

class Filters:

    def __init__(self, lot: ItemResponseInfo, traits: List[Trait], max_rank: int):
        self.lot = lot
        self.traits = traits
        self.max_rank = max_rank

    def filter_traits(self) -> Optional[ItemResponseInfo]:
        if self.traits:
            counter = 0
            for trait in self.lot.attributes:
                for asked_trait in self.traits:
                    if asked_trait == trait:
                        counter+=1
                        continue
            if counter == len(self.traits):
                return self.lot
            return None

    def filter_max_rank(self) -> Optional[ItemResponseInfo]:
        if self.lot.rarity.merarity.rank <= self.max_rank:
            return self.lot
        return None

    def use_filters(self) -> Optional[ItemResponseInfo]:
        logger.info("USE FILTER")
        if self.traits and self.max_rank > 0:
           if self.filter_traits() and self.filter_max_rank():
               logger.info('FILTERED TRAITS: {} MAX_RANK: {}'.format(self.traits, self.max_rank))
               return self.lot
        elif self.traits:
            logger.info('FILTERED TRAITS: {} MAX_RANK: {}'.format(self.traits, self.max_rank))
            if self.filter_traits():
                return self.lot
        elif self.max_rank > 0:
            if self.filter_max_rank():
                return self.lot
        else:
            return None

