import json, requests
from web3 import Web3
from os import getenv
from ...json_documents.pancake_router import router_abi
from ...json_documents.pancake_factory import factory_abi
from ...json_documents.pancake_pair import pair_abi
from ...json_documents.sell_abi import sell_abi



#BSC_API = getenv('bsc_apiKey') # <-- remove this getenv and put your abi here as str.

#BSC = "http://127.0.0.1:8545/"
BSC = "https://bsc-dataseed.binance.org/"
WEB3 = Web3(Web3.HTTPProvider(BSC))



router_abi = json.loads(router_abi)
factory_abi = json.loads(factory_abi)
sell_abi = json.loads(pair_abi)



class Address():
    '''This Class is Responsable for manage all Addresses. Except Websocket Addresses.'''
    def __init__(self, my_address , tokentobuy):
        self.my_address = WEB3.to_checksum_address(my_address)
        self.tokenBuy = WEB3.to_checksum_address(tokentobuy)
        self.router_abi = router_abi
        self.factory_abi = factory_abi
        self.sell_abi = sell_abi
        self.WBNB = WEB3.to_checksum_address("0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c")
        self.factory_address = WEB3.to_checksum_address("0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73")
        self.router_address = WEB3.to_checksum_address("0x10ED43C718714eb63d5aA57B78B54704E256024E")
        self.factory_contract = WEB3.eth.contract(address=self.factory_address, abi=factory_abi)
        self.contract_buy_sell = WEB3.eth.contract(address=self.router_address, abi=router_abi)
        self.token_abi = sell_abi
        self.pair_address = None
        self.pair_abi = None
        self.get_pair_abi()

    def get_pair_abi(self): 
        # Pair ABI
        self.pair_address = str(self.factory_contract.functions.getPair(self.WBNB, self.tokenBuy).call())
        self.pair_abi = sell_abi            
        return self.pair_abi