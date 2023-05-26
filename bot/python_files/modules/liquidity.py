import asyncio, json
from datetime import datetime

from modules.address import Address
from web3 import Web3
from os import getenv

BSC = "https://bsc-dataseed.binance.org/"
WEB3 = Web3(Web3.HTTPProvider(BSC))

#This class is responsable for check detect if the contract has liquidity or not, if has return True.
class Monitoring():
    '''This Class keeps listening for Mint function.'''
    def __init__(self, my_address, tokentobuy):
        self.all_address = Address(my_address, tokentobuy)
        self.running = True
        self.statusreturn = False
    
        #In order to know if the contract has liquidity, we need the pair address.
        if self.all_address.pair_abi:
            self.contract = WEB3.eth.contract(address=self.all_address.pair_address, abi=self.all_address.pair_abi)
        else:
            self.contract = None
    
    def breakwhile(self):
        '''Only to able and disable log_loop() from user interface.'''
        if self.running == True:
            self.running = False
        elif self.running == False:
            self.running = True

    async def log_loop(self, event_filter, poll_interval):
        '''loop to get the event_filter entries.'''
        print(self.all_address.pair_address)
        while self.running and self.statusreturn != True:
            entries = event_filter.get_new_entries()
            #if event_filter.get_new_entries() has any entry, the liquidity was added.
            if entries:
                self.statusreturn = True
                time2 = datetime.now().strftime('%d/%m/%y %H:%M:%S.%f')[:-3]
                print(f"catch something at {time2}")
                print(entries[0])
            await asyncio.sleep(poll_interval)
    
    def main(self):    
        if not self.contract:
            while self.running == True:
                self.all_address.get_pair_abi(self.all_address.tokenBuy)
                if self.contract:
                    self.statusreturn = True
                    time2 = datetime.now().strftime('%d/%m/%y %H:%M:%S.%f')
                    print(f'Catch sometghin at {time2}')
                    return self.statusreturn

        elif self.contract:
            self.statusreturn = False
            event_filter = self.contract.events.Mint.createFilter(fromBlock='latest')
            asyncio.set_event_loop(asyncio.new_event_loop())
            loop = asyncio.get_event_loop()
            try:
                loop.run_until_complete(
                    asyncio.gather(
                        self.log_loop(event_filter, 0)))
                return self.statusreturn
            finally:
                # close loop to free up system resources
                loop.close()