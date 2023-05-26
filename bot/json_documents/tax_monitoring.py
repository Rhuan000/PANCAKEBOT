import asyncio, json
import time
from time import sleep
from modules.address import Address
from web3 import Web3
from web3._utils.events import EventLogErrorFlags
from datetime import datetime

BSC = "https://bsc-dataseed.binance.org/"
WEB3 = Web3(Web3.HTTPProvider(BSC))

class Tax():
    def __init__(self, my_address, tokentobuy, window):
        self.all_address = Address(my_address, tokentobuy)
        self.window = window
        self.contract = WEB3.eth.contract(address=self.all_address.tokenBuy, abi=self.all_address.token_abi)
        self.pancakerouter_address = '0x10ED43C718714eb63d5aA57B78B54704E256024E'
        self.report = {}
        self.taxrunning = True
        self.old_report = {}
        self.result = ''
        self.hash = ''
        self.buytax = None
        self.selltax = None

    # define function to handle events and print to the console

    def handle_event(self, event):
        data_event = Web3.toJSON(event)
        data_event = json.loads(data_event)
        self.hash = data_event['transactionHash']
        try:
            self.result = WEB3.eth.getTransactionReceipt(self.hash)
        except:
            self.result = WEB3.eth.getTransactionReceipt('0x7c3343f4816bea30a03af4ceab23152d461026bd4879058d1ad45182abb002b4')


    def breakwhile(self):
        if self.taxrunning == True:
            self.taxrunning = False
        elif self.taxrunning == False:
            self.taxrunning = True


    def getting_report(self):
        logs = self.contract.events.Transfer().processReceipt(self.result, EventLogErrorFlags.Warn)
        total_from = {'from': [], 'to': [], 'amount': []}
        list_with_amount = []
        old_amount = ''

        for log in logs:
            transaction_type = log.event
            sender_address = log.args['from']
            destination_address = log.args['to']
            amount = log.args['value']

            total_from['from'].append(sender_address)
            total_from['to'].append(destination_address)
            total_from['amount'].append(float((WEB3.fromWei(amount, 'ether'))))

        gas_used_in_units = self.result['gasUsed']
        gas_price = WEB3.eth.gasPrice
        gas_used_in_wei = gas_used_in_units * gas_price
        gas_used_in_coin = float(WEB3.fromWei(gas_used_in_wei, 'ether'))
        total_in_amount = len(total_from['amount'])
        total_in_to = len(total_from['to'])

        print(total_from['amount'])
        try:
            if total_in_amount == 1:
                print('Only a Transfer.')
                tx_type = 'transfer'
                tx = 'transfer'

            elif total_from['amount'] == [10.9, 0.9, 10, 10]:
                tx_type = 'Loading'
                tx = 'Loading'
            elif total_from['amount'][0] == 0.0 and total_from['amount'][1] == 0.0:
                tx_type = 'Botspam'
                tx = 'Botspam'

            elif total_in_amount >= 3 and total_from['from'][0] == self.pancakerouter_address:
                try:
                    txatxype = self.default2(total_from, list_with_amount)
                    tx_type = txatxype[0]
                    tx = txatxype[1]
                except:
                    tx_type = 'cant detect'
                    tx = 'cant detect'

            elif total_in_amount >= 3 and self.all_address.tokenBuy == total_from['from'][0]:
                try:
                    txatxype = self.default3(total_from, list_with_amount)
                    tx_type = txatxype[0]
                    tx = txatxype[1]
                except:
                    tx_type = 'cant detect'
                    tx = 'cant detect'

            elif total_in_amount >= 3 and self.all_address.tokenBuy in total_from['to']:
                try:
                    txatxype = self.default4(total_from, list_with_amount)
                    tx_type = txatxype[0]
                    tx = txatxype[1]
                except:
                    tx_type = 'cant detect'
                    tx = 'cant detect'

            elif total_in_amount > 1 and total_from['from'][0] == self.pancakerouter_address or total_from['from'][len(total_from['from'])-1] or total_from['to'][len(total_from['to'])-1]:
                try:
                    txatxype = self.default5(total_from, list_with_amount, sender_address, total_in_amount)
                    tx_type = txatxype[0]
                    tx = txatxype[1]
                except ZeroDivisionError:
                    tx_type = txatxype[0]
                    tx = '0.0'
                except:
                    tx_type = 'cant detect'
                    tx = 'cant detect'

            elif total_in_amount >= 3 and total_from['to'][total_in_to - 1] == self.pancakerouter_address:
                try:
                    txatxype = self.default1(total_from, list_with_amount)
                    tx_type = txatxype[0]
                    tx = txatxype[1]
                except:
                    tx_type = 'cant detect'
                    tx = 'cant detect'
            else:
                print(total_in_amount)
                tx_type = 'cant detect'
                tx = 'cant detect'

            if tx != 'cant detect' and tx != 'transfer':
                if tx_type == 'BuyTax':
                    self.buytax = tx
                else:
                    self.selltax = tx

            self.report = {
                      'transactionType': transaction_type,
                      'from': sender_address,
                      'to': destination_address,
                      'transactionHash': self.hash,
                      'GasUsed': gas_used_in_units,
                      'TransactionFee': gas_used_in_coin,
                      'taxtype': tx_type,
                      'tax': f'{tx}%',
                      'time': self.time}
        except IndexError:
            print('skipped')

    # asynchronous defined function to loop
    # this loop sets up an event filter and is looking for new entires for the "PairCreated" event
    # this loop runs on a poll interval
    async def log_loop(self, event_filter, poll_interval):
            while self.taxrunning:
                self.window.update()
                new_entries = event_filter.get_new_entries()
                quantidade = len(new_entries)
                self.time = datetime.now().strftime('%d/%m/%y %H:%M:%S')

                if quantidade != 0:
                    print(quantidade)
                    inicio = time.time()
                    self.handle_event(new_entries[len(new_entries) - 1])
                    self.getting_report()
                    contador = 0
                    while self.report['taxtype'] == 'Loading' and contador != 4:
                        self.handle_event(new_entries[len(new_entries)-1])
                        self.getting_report()
                        contador += 1
                if self.report != self.old_report:
                    print(self.report)
                    fim_total = time.time()
                    print(f'tempo de análise: {fim_total-inicio}')
                self.old_report = self.report
                await asyncio.sleep(poll_interval)

    # when main is called
    # create a filter for the latest block and look for the "PairCreated" event for the uniswap factory contract
    # run an async loop
    # try to run the log_loop function above every 2 seconds
    def main(self):
        event_filter = self.contract.events.Transfer.createFilter(address=self.all_address.tokenBuy, fromBlock='latest')
        # block_filter = web3.eth.filter('latest')
        # tx_filter = web3.eth.filter('pending')
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            print('Listening for tax')
            loop.run_until_complete(
                asyncio.gather(
                    self.log_loop(event_filter, 0)))
            # log_loop(block_filter, 2),
            # log_loop(tx_filter, 2)))
        finally:
            # close loop to free up system resources
            loop.close()
            print('Dont listening')

    #Calculos de porcentagem através dos padrões de hashs.
    def default1(self,total_from, list_with_amount):
        print('padrão 1')

        firstFrom = total_from['from'][0]

        contador = 0
        for address in total_from['from']:

            if address == firstFrom:
                list_with_amount.append(total_from['amount'][contador])
            contador += 1
        soma = 0
        for amount in list_with_amount[0:len(list_with_amount) - 1]:
            soma += amount

        if len(list_with_amount) >= 2:
            amount_gived = float(WEB3.fromWei(soma, 'ether'))
            amount_receveid = float(WEB3.fromWei(list_with_amount[len(list_with_amount) - 1], 'ether'))
            final_amount = amount_receveid + amount_gived
            tx_type = 'SellTax'
            tx = round((amount_gived * 100) / final_amount, 2)
        else:
            firstTo = total_from['to'][0]

            contador = 0
            for address in total_from['to']:
                amount_to_list = total_from['amount'][contador]
                if address == firstTo and amount_to_list not in list_with_amount:
                    list_with_amount.append(amount_to_list)
                contador += 1

            soma = 0
            for amount in list_with_amount[0:len(list_with_amount) - 1]:
                soma += amount

            if len(list_with_amount) >= 2:
                amount_gived = float(WEB3.fromWei(soma, 'ether'))
                amount_receveid = float(WEB3.fromWei(list_with_amount[len(list_with_amount) - 1], 'ether'))
                final_amount = amount_receveid + amount_gived
                tx_type = 'SellTax'
                tx = round((amount_gived * 100) / final_amount, 2)
            else:
                tx_type = 'Cant check'
                tx = 'Cant check'
        return tx_type, tx
    def default2(self,total_from, list_with_amount):
        print('padrão 2')
        firstTo = total_from['to'][0]

        contador = 0
        for address in total_from['from']:
            if address == firstTo:
                list_with_amount.append(total_from['amount'][contador])
            contador += 1

        soma = 0
        for amount in list_with_amount[0:len(list_with_amount) - 1]:
            soma += amount

        amount_gived = float(WEB3.fromWei(soma, 'ether'))
        amount_receveid = float(WEB3.fromWei(list_with_amount[len(list_with_amount) - 1], 'ether'))
        final_amount = amount_receveid + amount_gived
        tx_type = 'BuyTax'
        tx = round((amount_gived * 100) / final_amount, 2)
        return tx_type, tx
    def default3(self,total_from, list_with_amount):
        print('padrão 3')
        firstFrom = total_from['from'][0]

        contador = 0
        for address in total_from['to']:
            if address == firstFrom:
                secondFrom = total_from['from'][contador]
            contador += 1

        contador2 = 0
        amount_receveid = 0
        for address in total_from['from']:
            if address == secondFrom and total_from['to'][contador2] == firstFrom:
                amount_receveid += float(total_from['amount'][contador2])

            if address == secondFrom:
                list_with_amount.append(total_from['amount'][contador2])
            contador2 += 1
        soma = 0
        for amount in list_with_amount[0:len(list_with_amount) - 1]:
            soma += amount

        amount_gived = float(WEB3.fromWei(soma, 'ether'))
        amount_receveid = float(WEB3.fromWei(list_with_amount[len(list_with_amount) - 1], 'ether'))
        final_amount = amount_receveid + amount_gived
        tx_type = 'SellTax'
        tx = round((amount_gived * 100) / final_amount, 2)
        return tx_type, tx
    def default4(self, total_from, list_with_amount):
        list_wasub = [] 
        print('padrão 4')
        contador = 0
        for addres in total_from['to']:
            if addres == self.all_address.tokenBuy:
                list_wasub.append(total_from['amount'][contador])
                list_with_amount.append(total_from['amount'][contador + 1])

            contador += 1

        soma = 0
        for amount in list_with_amount:
            soma += amount

        soma2 = 0
        for amount in list_wasub:
            soma2 += amount

        amount_gived = float(WEB3.fromWei(soma2, 'ether'))
        amount_receveid = float(WEB3.fromWei(soma, 'ether'))
        final_amount = amount_receveid + amount_gived

        if list_with_amount[len(list_with_amount) - 1] == total_from['amount'][len(total_from['amount']) - 1]:
            tx_type = 'BuyTax'
        else:
            tx_type = 'SellTax'
        tx = round((amount_gived * 100) / final_amount, 2)
        return tx_type, tx
    def default5(self, total_from, list_with_amount, sender_address, total_in_amount):
        list_wabs = []
        print('padrão 5')
        firstTo = total_from['to'][0]
        lastTo = total_from['to'][len(total_from['to']) - 1]

        contador = 0
        for address in total_from['from']:
            if address == firstTo:
                firstTo = total_from['to'][contador]
                list_with_amount.append(total_from['amount'][contador])
                list_wabs.append(total_from['amount'][contador + 1])

        soma = 0
        for amount in list_with_amount[0:len(list_with_amount) - 1]:
            soma += amount

        soma2 = 0
        for amount in list_wabs:
            soma += amount
        amount_gived = float(WEB3.fromWei(soma, 'ether'))
        amount_receveid = float(WEB3.fromWei(soma2, 'ether'))
        if total_in_amount == 2:
            amount_gived = float(WEB3.fromWei(soma2, 'ether'))
            amount_receveid = float(WEB3.fromWei(soma, 'ether'))

        if lastTo == self.pancakerouter_address:
            amount_gived = float(WEB3.fromWei(soma2, 'ether'))
            amount_receveid = float(WEB3.fromWei(soma, 'ether'))
            tx_type = 'SellTax'

        else:
            tx_type = 'BuyTax'
        final_amount = amount_receveid + amount_gived
        if final_amount != 0:
            tx = round((amount_gived * 100) / final_amount, 2)
        else:
            tx = '0.0'
        return tx_type, tx
