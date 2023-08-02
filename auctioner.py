from pyinjective.composer import Composer as ProtoMsgComposer
from pyinjective.async_client import AsyncClient
from pyinjective.transaction import Transaction
from pyinjective.constant import Network
from pyinjective.wallet import PublicKey, Address, PrivateKey

from creds import WALLET_KEY
import settings


mainnet_nodes = [
    'lb', # us, asia, prod
    'sentry0',  # ca, prod
    'sentry1',  # ca, prod
    'sentry3',  # us, prod
]


class Auctioner:
    network: Network
    composer: ProtoMsgComposer
    client: AsyncClient
    priv_key: PrivateKey
    pub_key: PublicKey
    address: Address
    def __init__(self, network: Network, composer: ProtoMsgComposer, client: AsyncClient, priv_key: PrivateKey, pub_key: PublicKey, address: Address):
        self.network = network
        self.composer = composer
        self.client = client
        self.priv_key = priv_key
        self.pub_key = pub_key
        self.address = address

    @classmethod
    async def create(cls):
        network, client = cls.get_network_and_client()
        await client.sync_timeout_height()
        composer = ProtoMsgComposer(network=network.string())
        priv_key = PrivateKey.from_hex(WALLET_KEY)
        pub_key = priv_key.to_public_key()
        address = pub_key.to_address()
        account = await client.get_account(address.to_acc_bech32())
        return cls(network, composer, client, priv_key, pub_key, address)

    @classmethod
    def get_network_and_client(cls):
        if settings.BROADCAST_NODE in mainnet_nodes:
            network = Network.mainnet(settings.BROADCAST_NODE)
            return AsyncClient(network, insecure=(False if settings.BROADCAST_NODE == "lb" else True))
        if settings.BROADCAST_NODE == "local":
            network = Network.local()
        else:
            network = Network.custom(
                lcd_endpoint=f'http://{settings.BROADCAST_NODE}:10337',
                tm_websocket_endpoint=f'ws://{settings.BROADCAST_NODE}:26657/websocket',
                grpc_endpoint=f'{settings.BROADCAST_NODE}:9900',
                grpc_exchange_endpoint=f'{settings.BROADCAST_NODE}:9910',
                grpc_explorer_endpoint=f'{settings.BROADCAST_NODE}:9911',
                chain_id='injective-1',
                env='mainnet'
            )
        return network, AsyncClient(network, insecure=True)

    async def broadcast_auction(self, bid_: float):
        msg = self.composer.MsgBid(
            sender=self.address.to_acc_bech32(),
            round=settings.ROUND,
            bid_amount=bid_
        )

        # build sim tx
        tx = (
            Transaction()
            .with_messages(msg)
            .with_sequence(self.client.get_sequence())
            .with_account_num(self.client.get_number())
            .with_chain_id(self.network.chain_id)
        )
        sim_sign_doc = tx.get_sign_doc(self.pub_key)
        sim_sig = self.priv_key.sign(sim_sign_doc.SerializeToString())
        sim_tx_raw_bytes = tx.get_tx_data(sim_sig, self.pub_key)

        # simulate tx
        (sim_res, success) = await self.client.simulate_tx(sim_tx_raw_bytes)
        if not success:
            print(sim_res)
            return

        # build tx
        gas_price = 500000000
        gas_limit = sim_res.gas_info.gas_used + 25000  # add 25k for gas, fee computation
        gas_fee = '{:.18f}'.format((gas_price * gas_limit) / pow(10, 18)).rstrip('0')
        fee = [self.composer.Coin(
            amount=gas_price * gas_limit,
            denom=self.network.fee_denom,
        )]
        tx = tx.with_gas(gas_limit).with_fee(fee).with_memo('').with_timeout_height(self.client.timeout_height)
        sign_doc = tx.get_sign_doc(self.pub_key)
        sig = self.priv_key.sign(sign_doc.SerializeToString())
        tx_raw_bytes = tx.get_tx_data(sig, self.pub_key)

        # broadcast tx: send_tx_async_mode, send_tx_sync_mode, send_tx_block_mode
        res = await self.client.send_tx_async_mode(tx_raw_bytes)
        print(res)
        print("gas wanted: {}".format(gas_limit))
        print("gas fee: {} INJ".format(gas_fee))