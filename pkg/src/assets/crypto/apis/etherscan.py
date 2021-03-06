import os
from typing import List, Union

import aiohttp

from web3 import Web3


def wei_to_ether(wei) -> float:
    return float(Web3.fromWei(int(wei), 'ether'))


class EtherScan:
    API_URL = 'https://api.etherscan.io'
    BALANCES = {}

    def __init__(self, session: aiohttp.ClientSession):
        self.api_key = os.environ['ETHERSCAN_API_KEY']
        self.session = session

    def _build_url(self, **kwargs) -> str:
        kwargs.update({'apikey': self.api_key})
        params = '&'.join(f'{k}={v}' for k, v in kwargs.items())
        return f'{self.API_URL}/api?{params}'

    async def _send(self, request, **kwargs) -> dict:
        async with request(url=self._build_url(**kwargs)) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def get_ether_balance(self, address: str) -> float:
        return await self.get_ether_balances(address, return_sum=True)

    async def get_ether_balances(self, *addresses, return_sum: bool = False) -> Union[float, List[dict]]:
        params = {'module': 'account', 'action': 'balancemulti', 'address': ','.join(addresses)}
        retval = await self._send(self.session.get, **params)
        accounts = retval['result']
        if not return_sum:
            for account in accounts:
                account['balance'] = wei_to_ether(account['balance'])
            return accounts
        return wei_to_ether(sum(int(acct['balance']) for acct in accounts))

    async def get_token_balance(self, address: str, contract_address: str) -> float:
        params = {
            'action': 'tokenbalance',
            'address': address,
            'contractaddress': contract_address,
            'module': 'account',
            'tag': 'latest'
        }
        retval = await self._send(self.session.get, **params)
        return wei_to_ether(retval['result'])
