from web3 import Web3
from modules.address import Address

bsc = "https://bsc-dataseed.binance.org/"
web3 = Web3(Web3.HTTPProvider(bsc))

class GetInteraction():
    '''the Methods inside this class will return the token Value, Name and the quantity of token (BNB or token you want to buy) that you have. '''
    def __init__(self, my_address, tokentobuy):
        self.all_adress = Address(my_address, tokentobuy)
        self.token_price: float
        self.symbol_of_token = self.getTokenSymbol()


    def getTokenPrice(self) -> float:
        tokenRouter = web3.eth.contract(address=self.all_adress.tokenBuy, abi=self.all_adress.get_pair_abi())
        tokenDecimals = tokenRouter.functions.decimals().call()
        tokensToSell = int(str(1).ljust(tokenDecimals + len(str(1)), '0'))



        router = web3.eth.contract(address=self.all_adress.router_address, abi=self.all_adress.router_abi)
        amountOut = router.functions.getAmountsOut(tokensToSell, [self.all_adress.tokenBuy, self.all_adress.WBNB]).call()
        amountOut = web3.fromWei(amountOut[1], 'ether')
        self.token_price = float(amountOut)
        return self.token_price



    def getTokenSymbol(self) -> str:
        contract_token = web3.eth.contract(address=self.all_adress.tokenBuy, abi=self.all_adress.token_abi)
        self.symbol_of_token = contract_token.functions.symbol().call().split()[0]
        return self.symbol_of_token

    def get_balance(self):
        #BNB Balance
        balance = web3.eth.get_balance(self.all_adress.my_address)
        bnb_balance = web3.fromWei(balance, 'ether')

        #Token To buy Balance
        sellTokenContract = web3.eth.contract(self.all_adress.tokenBuy, abi=self.all_adress.sell_abi)
        balance2 = sellTokenContract.functions.balanceOf(self.all_adress.my_address).call()
        token_balance = web3.fromWei(balance2, 'ether')

        return bnb_balance, token_balance