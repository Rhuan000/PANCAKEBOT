import json, requests
from web3 import Web3
from dotenv import load_dotenv
from os import getenv 

#YOU NEED TO PROVIDE YOUR BSC_API TO GET THE token  and pair ABI. 
load_dotenv()

BSC_API = getenv('bsc_apiKey') # <-- remove this getenv and put your abi here as str.
URL_ETH = "https://api.bscscan.com/api"
BSC = "https://bsc-dataseed.binance.org/"
WEB3 = Web3(Web3.HTTPProvider(BSC))



with open('../json_documents/pancake_router.json', 'r') as token_data:
    router_abi = json.load(token_data)
#pancake router ABI
with open('../json_documents/pancake_factory.json', 'r') as factory_data:
    factory_abi = json.load(factory_data)
#sell_abi
with open('../json_documents/sell_abi.json', 'r') as sell_data:
    sell_abi = json.load(sell_data)



class Address():
    '''This Class is Responsable for manage all Addresses. Except Websocket Addresses.'''
    def __init__(self, my_address , tokentobuy):
        self.my_address = WEB3.toChecksumAddress(my_address)
        self.tokenBuy = WEB3.toChecksumAddress(tokentobuy)
        self.router_abi = router_abi
        self.factory_abi = factory_abi
        self.sell_abi = sell_abi
        self.WBNB = WEB3.toChecksumAddress("0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c")
        self.factory_address = WEB3.toChecksumAddress("0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73")
        self.router_address = WEB3.toChecksumAddress("0x10ED43C718714eb63d5aA57B78B54704E256024E")
        self.factory_contract = WEB3.eth.contract(address=self.factory_address, abi=factory_abi)
        self.contract_buy_sell = WEB3.eth.contract(address=self.router_address, abi=router_abi)
        self.token_abi = self.get_token_abi()
        self.pair_address = None
        self.pair_abi = None
        self.get_pair_abi()

    def get_pair_abi(self): 
        # Pair ABI
        self.pair_address = str(self.factory_contract.functions.getPair(self.WBNB, self.tokenBuy).call())
        abi_pair_endpoint = f"{URL_ETH}?module=contract&action=getabi&address={str(self.pair_address)}&apikey={BSC_API}"
        pair_data = requests.get(url=abi_pair_endpoint)
        pair_response = pair_data.json()
        if self.pair_address != "0x0000000000000000000000000000000000000000":
            self.pair_abi = json.loads(pair_response["result"])
            return self.pair_abi
        else:
            print('Pair address was not created.')

    def get_token_abi(self):
        tokenabi_endpoint = f"{URL_ETH}?module=contract&action=getabi&address={str(self.tokenBuy)}&apikey={BSC_API}"
        token_abidata = requests.get(url=tokenabi_endpoint)
        response = token_abidata.json()
        loads = json.loads(response['result'])
        self.token_abi = loads
        return self.token_abi