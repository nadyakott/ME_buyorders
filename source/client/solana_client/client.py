from solana.publickey import PublicKey
from solana.transaction import TransactionInstruction, AccountMeta, Transaction
from solana.rpc.api import Client, types, Commitment
from solana.rpc.async_api import AsyncClient
from solana.keypair import Keypair
from typing import Union, Any, List
from libs.settings import settings


class AsyncSolanaClient:

    def __init__(self, connection: str):
        self.connection_str = connection
        self.client = AsyncClient(endpoint=connection)

    async def send_transaction(self, data: Union[List[int]]):
        '''
            при инициализации ставки на покупку
            пример: https://api-mainnet.magiceden.io/v2/instructions/buy_and_deposit?price=0.01&buyer=D9PkuGfwNgWKuaTEVR8G7dUMYrnhRSbk8ELb41whCEiN&auctionHouseAddress=E8cU1WiRWjanGxmn96ewBgk9vPTcL6AEZ1t6F6fkgUWe&tokenMint=AG6kNVQAhcip27FxY5LNE3kPML4drghGXePyJHrUDshh
            magic eden возвращает в ответ транзакцию, которую нужно подписать (sign)
        :param data: ответ от magic eden массив на 560 элементов типа децимал,
        это + signer (sender) мы отдаем в инфраструктуру соланы
        :return: на выходе получаем transaction signature
        '''
        async with self.client as client:
            full_signed_tx_hex = bytes(data).hex()
            tx = Transaction.deserialize(bytes.fromhex(full_signed_tx_hex))
            sender = Keypair.from_secret_key(bytes.fromhex(settings.PRIVATE_KEY))

            response = (await client.send_transaction(tx, sender)).value
            return response
