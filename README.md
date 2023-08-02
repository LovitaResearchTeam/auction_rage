# auction_rage
This project aims to get auctions of [Injective Exchange](https://injective.com/), a blockchain built for finance.

## settings.py
To write your own settings, you need to make a copy of `settings.py.example` and name it `settings.py`.

- `ROUND` : Specifies which auction round you want to participate.
- `DATE` : Indicates when the auction ends.
- `BROADCAST_NODE`: Indicates in which injective node you want to send corresponding tx. (eg: lb, sentry0, ... or the exact address of a node (for example 127.0.0.1))
- `WS_NODE`: Indicates the node you want to receive stream from.
- `MAX_ALLOWED_BID` : The final amount you want to raise your bid to.
- `RAISE_BID` : The amount of bid you want to raise when another bid is on yours.


## creds.py
To write your own credentials, you need to make a copy of `creds.py.example` and name it `creds.py`.

Good Luck.
