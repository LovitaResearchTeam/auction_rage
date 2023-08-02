from typing import Coroutine
from pyinjective.async_client import AsyncClient
from pyinjective.constant import Network

import settings

mainnet_nodes = [
    'lb',
    'sentry0',
    'sentry1',
    'sentry3',
]

class BidSocketHandler:
    handler: Coroutine
    def __init__(self, handler: Coroutine) -> None:
        self.handler = handler

    @staticmethod
    def init_ws_client(node: str) -> AsyncClient:
        if node in mainnet_nodes:
            network = Network.mainnet(node)
            return AsyncClient(network, insecure=(False if node == "lb" else True))
        if node == "local":
            network = Network.local()
        else:
            network = Network.custom(
                lcd_endpoint=f'http://{node}:10337',
                tm_websocket_endpoint=f'ws://{node}:26657/websocket',
                grpc_endpoint=f'{node}:9900',
                grpc_exchange_endpoint=f'{node}:9910',
                grpc_explorer_endpoint=f'{node}:9911',
                chain_id='injective-1',
                env='mainnet'
            )
        return AsyncClient(network, insecure=True)

    async def run(self):
        print("Running!")
        client = self.init_ws_client(settings.WS_NODE)
        await self.starter()
        bids = await client.stream_bids()
        async for bid in bids:
            await self.handler(bid)

    async def starter(self):
        network = Network.mainnet()
        client = AsyncClient(network, insecure=False)
        auction = await client.get_auction(bid_round=settings.ROUND)
        return await self.handler(auction.bids[-1])