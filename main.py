import asyncio
import traceback
import time

from google.protobuf.json_format import MessageToDict

from auctioner import Auctioner
from bid_socket_handler import BidSocketHandler
from creds import ADDRESS
import settings


async def main():
    while True:
        try:
            auctioner = await Auctioner.create()
            async def handler(msg):
                the_bid = MessageToDict(msg)
                print("MSG:", msg)
                print()
                bidder = the_bid['bidder']
                if bidder == ADDRESS:
                    print("This is our address. So we do not trade.")
                    return
                if 'round' in the_bid:
                    if not settings.ROUND == int(the_bid['round']):
                        print("Wrong round")
                        return
                bid_amount = round(float(the_bid['bid_amount' if 'bid_amount' in the_bid else 'amount']) * 10**(-18), 1)
                bid_amount += settings.RAISE_BID
                if bid_amount > settings.MAX_ALLOWED_BID:
                    print("bid_amount more than max allowed:", bid_amount)
                    return
                await auctioner.broadcast_auction(bid_amount)
            socket_handler = BidSocketHandler(handler)
            await socket_handler.run()
        except:
            traceback.print_exc()
            time.sleep(1)



if __name__ == "__main__":
    asyncio.run(main())
            