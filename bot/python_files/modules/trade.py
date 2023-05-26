from modules.token_interaction import GetInteraction
from web3 import Web3
from modules.address import Address
import time
from  eth_account import Account

BSC = "https://bsc-dataseed.binance.org/"
WEB3 = Web3(Web3.HTTPProvider(BSC))

class Trade():
    def __init__(self, PRIVATE_KEY, my_address, tokentobuy):
        self.all_address = Address(my_address, tokentobuy)
        self.price = GetInteraction(my_address, tokentobuy)
        self.private_key = PRIVATE_KEY
        self.gweibuy = '9'
        self.gweisell = '8'
        self.token_price: str
        self.buy_contract_address: str
        self.sell_contract_address: str

    def check_Private_key(self):
        pa = Account.from_key(self.private_key)
        # Get public address from a signer wallet
        publicAddress = pa.address
        if self.all_address.my_address == publicAddress:
            return True
        else:
            return False

    def buy(self, how_much_bnb_want_spend):

        pancakeswap2_txn = self.all_address.contract_buy_sell.functions.swapExactETHForTokensSupportingFeeOnTransferTokens(
            0,  # set to 0, or specify minimum amount of tokeny you want to receive - consider decimals!!!
            [self.all_address.WBNB, self.all_address.tokenBuy],
            self.all_address.my_address,
            (int(time.time() + 10000))
        ).buildTransaction({
            'from': self.all_address.my_address,
            'value': WEB3.toWei(how_much_bnb_want_spend, 'ether'),  # This is the Token(BNB) amount you want to Swap from
            'gas': 1500000,
            'gasPrice': WEB3.toWei(self.gweibuy, 'gwei'),
            'nonce': WEB3.eth.get_transaction_count(self.all_address.my_address)
        })
        signed_txn = WEB3.eth.account.sign_transaction(pancakeswap2_txn, private_key=self.private_key)
        tx_token = WEB3.eth.send_raw_transaction(signed_txn.rawTransaction)
        self.token_price = self.price.getTokenPrice()
        self.buy_contract_address = f" BUY CONTRACT: {WEB3.toHex(tx_token)}"

        with open('../token_price_at_trade.txt', 'w') as data:
            data.write(str(self.token_price))

    'quantity'
    def sell(self, quantity: float):
        sellTokenContract = WEB3.eth.contract(self.all_address.tokenBuy, abi=self.all_address.sell_abi)

        # Get Token Balance
        balance = sellTokenContract.functions.balanceOf(self.all_address.my_address).call()
        symbol = sellTokenContract.functions.symbol().call()
        readable = WEB3.fromWei(balance, 'ether')
        readable = round(float(readable), 3)-0.001


        #amount of token to sell
        tokenValue = WEB3.toWei(quantity, 'ether')

        # Approve Token before Selling
        tokenValue2 = WEB3.fromWei(tokenValue, 'ether')

        approve = sellTokenContract.functions.approve(self.all_address.router_address, balance).buildTransaction({
            'from': self.all_address.my_address,
            'gasPrice': WEB3.toWei(self.gweisell, 'gwei'),
            'nonce': WEB3.eth.get_transaction_count(self.all_address.my_address),
        })
        signed_txn = WEB3.eth.account.sign_transaction(approve, private_key=self.private_key)
        tx_token = WEB3.eth.send_raw_transaction(signed_txn.rawTransaction)
        self.sell_contract_address  = f"SELL CONTRACT: {WEB3.toHex(tx_token)}"

        # Wait after approve 5 seconds before sending transaction
        time.sleep(2)

        # Swaping exact Token for ETH
        pancakeswap2_txn = self.all_address.contract_buy_sell.functions.swapExactTokensForETHSupportingFeeOnTransferTokens(
            tokenValue, 0,
            [self.all_address.tokenBuy, self.all_address.WBNB],  # token address to sell, and the token address you want to receive
            self.all_address.my_address,
            (int(time.time()) + 1000000)

        ).buildTransaction({
            'from': self.all_address.my_address,
            'gas': 1500000,
            'gasPrice': WEB3.to.Wei(self.gweisell, 'gwei'),
            'nonce': WEB3.eth.get_transaction_count(self.all_address.my_address),
        })

        signed_txn = WEB3.eth.account.sign_transaction(pancakeswap2_txn, private_key=self.private_key)
        tx_token = WEB3.eth.send_raw_transaction(signed_txn.rawTransaction)