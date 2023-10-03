import tkinter, threading
from tkinter import messagebox, ttk
from bot.python_files.modules.token_interaction import GetInteraction
from bot.python_files.modules.trade import Trade
from bot.python_files.modules.liquidity import Monitoring
import datetime as dt

class GUI():

    def __init__(self):
        self.wc_connected = 0
        self.testvalue = 0
        
        
        self.wallets = []
        self.bnb_in_account = []
        self.token_in_account = []
        self.trade:[Trade] = []
        self.interaction = []
        self.liquidity = []
        #self.taxmonitor = []
        
        
        self.state = False
        self.automatic_running = False
        self.buy_running = False
        self.sell_running = False
        
        self.momentTime = None
        self.newWindow = None
        self.kept_return: bool
        
        self.wallet_index = 0 #This will change with the list wallets.Keeping track.
        self.symbol = 'SYMBOL'

        #Creating a Window
        self.window = tkinter.Tk()
        self.window.title('PancakeBot')

        self.window.geometry("700x600+350+25")
        self.window.config(padx=15, pady=30)


        self.separator = ttk.Separator(orient='horizontal', class_= "ttk.separator")
        self.separator.grid(row=7)

        # first label
        self.status_label = tkinter.Label(text="Disconnected", fg="red", font=('Roboto', 25))
        self.status_label.grid(column=1, row=0)
        self.hour_label = tkinter.Label(text="00:00", fg="black", font=('Roboto', 15))
        self.hour_label.grid(column=0, row=1)

        # canvas
        self.canvas = tkinter.Canvas(width=161, height=169)
        # Get the directory of the current script
        import sys, os
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)


        image_path = os.path.join(application_path, '../pancakecanvas.png')

        self.logo_img = tkinter.PhotoImage(file=image_path)
        self.canvas.create_image(80.5, 84.5, image=self.logo_img)
        self.canvas.grid(column=1, row=1, padx=10, pady=10)

# -------------------------------------------------- CONNECT FRAME START --------------------------------------------------#
        self.connectFrame = tkinter.Frame(relief='groove', bd=1, height=116, width=500)
        self.connectFrame.grid_propagate(0)
        self.connectFrame.grid(column=1, row=2)
        #Connect Labels
        self.secretk_ConnectLabel = tkinter.Label(self.connectFrame, text='Secret Key:')
        self.secretk_ConnectLabel.grid(column=0, row=0)
        self.wallet_ConnectLabel = tkinter.Label(self.connectFrame, text='Wallet Address:')
        self.wallet_ConnectLabel.grid(column=0, row=1)
        self.token_ConnectLabel = tkinter.Label(self.connectFrame, text='Token Address:')
        self.token_ConnectLabel.grid(column=0, row=2)
        #Connect Entries
        self.secretKey_ConnectEntry = tkinter.Entry(self.connectFrame, width=48)
        self.secretKey_ConnectEntry.grid(column=1, row=0, columnspan=2)
        self.secretKey_ConnectEntry.config(show="•")
        self.secretKey_ConnectEntry.focus()
        self.wtAddress_ConnectEntry = tkinter.Entry(self.connectFrame, width=48)
        self.wtAddress_ConnectEntry.grid(column=1, row=1, columnspan=2)
        self.tkAddress_ConnectEntry = tkinter.Entry(self.connectFrame, width=48)
        self.tkAddress_ConnectEntry.insert(0, '0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56') # <---  this is the BUSD address
        self.tkAddress_ConnectEntry.grid(column=1, row=2, columnspan=2)


        #Connect Buttons

        self.connect_ConnectButton = tkinter.Button(self.connectFrame, text="Connect", command=self.saveEntry, width=20, state="disabled")
        self.connect_ConnectButton.grid(column=1, row=3)
        self.addwallet_ConnectButton = tkinter.Button(self.connectFrame, text="Add Wallet", command=self.addingwallet, width=20)
        self.addwallet_ConnectButton.grid(column=2, row=3)
# -------------------------------------------------- CONNECT FRAME FINAL --------------------------------------------------#

# -------------------------------------------------- LISTBOX  FRAME Connected ---------------------------------------

        self.listboxFrame = tkinter.Frame(relief='groove', bd=1, height=100, width=110, padx=6)
        self.listboxFrame.grid_propagate(0)
        self.listboxFrame.grid(column=0, row=2)
        
        
        # Label
        self.wc_ListboxLabel = tkinter.Label(self.listboxFrame, text=f'Wallets {self.wc_connected}')
        self.wc_ListboxLabel.pack(side='top')

        # Scroll bar and listbox
        self.listbox_ListboxListbox = tkinter.Listbox(self.listboxFrame, height=6, width=11, state='disabled')
        self.listbox_ListboxListbox.pack(side = 'left', fill = 'both')
        self.scroll_ListboxScroll = tkinter.Scrollbar(self.listboxFrame)
        self.scroll_ListboxScroll.pack(side = 'right', fill = 'both')
        self.listbox_ListboxListbox.config(yscrollcommand= self.scroll_ListboxScroll.set)
        self.scroll_ListboxScroll.config(command= self.listbox_ListboxListbox.yview)
        self.listbox_ListboxListbox.bind('<<ListboxSelect>>', self.immd)#Just to interact with the listbox



# -------------------------------------------------- WALLET FRAME START --------------------------------------------------#
        self.walletFrame = tkinter.Frame(relief='groove', bd=1, height=120, width=110, padx=6)
        self.walletFrame.grid(column=0, row=3)
        self.walletFrame.grid_propagate(0)

        self.title_WalletLabel = tkinter.Label(self.walletFrame, text=f'Wallet:')
        self.title_WalletLabel.grid(column=0, row=0)
        self.bnbAmount_WalletLabel = tkinter.Label(self.walletFrame, text=f'0 BNB')
        self.bnbAmount_WalletLabel.grid(column=0, row=1)
        self.tokenAmount_Walletlabel = tkinter.Label(self.walletFrame, text=f'0 {self.symbol}')
        self.tokenAmount_Walletlabel.grid(column=0, row=2)

        self.update_WalletButton = tkinter.Button(self.walletFrame, text='update', command=self.updateButtonTrigged)
        self.update_WalletButton.grid(row=3, column=0, columnspan=2)

# -------------------------------------------------- WALLET FRAME FINAL --------------------------------------------------#


#-------------------------------------------------- TRADE FRAME START --------------------------------------------------#
        self.tradeFrame = tkinter.Frame(relief='groove', height=190, width=500, bd=1)
        self.tradeFrame.grid_propagate(0)
        self.tradeFrame.grid(column=1, row=3, rowspan=2)

        #Trade Labels
        self.bnbToSpend_TradeLabel = tkinter.Label(self.tradeFrame, text=f'BNB')
        self.bnbToSpend_TradeLabel.grid(column=0, row=1)


        self.profit100_TradeLabel = tkinter.Label(self.tradeFrame, text='%')
        self.profit100_TradeLabel.grid(column=2, row=2)

        self.symboltrade_TradeLabel = tkinter.Label(self.tradeFrame, text=f'{self.symbol}')
        self.symboltrade_TradeLabel.grid(column=3, row=1)

        self.pricetrade_TradeLabel = tkinter.Label(self.tradeFrame, text=f'PRICE/EA')
        self.pricetrade_TradeLabel.grid(column=3, row=2)

        self.pricetradebnb_TradeLabel = tkinter.Label(self.tradeFrame, text=f'$BNB')
        self.pricetradebnb_TradeLabel.grid(column=5, row=2)

        self.gweibuy_TradeLabel = tkinter.Label(self.tradeFrame, text='Gwei Buy')
        self.gweibuy_TradeLabel.grid(column=2, row=3)

        self.gweisell_TradeLabel = tkinter.Label(self.tradeFrame, text='Gwei Sell')
        self.gweisell_TradeLabel.grid(column=4, row=3)


        # Trade Buttons
        self.arrow_TradeButton = tkinter.Button(self.tradeFrame, text='≅', width=3, height=1, state='disabled', command=self.exchange)
        self.arrow_TradeButton.grid(column=2, row=1)

        self.buy_TradeButton = tkinter.Button(self.tradeFrame, text='Buy', width=7, height=1, bg='#66CDAA',activebackground='#008080', state='disabled', command=self.catch_buy_button)
        self.buy_TradeButton.grid(column=4, row=4)

        self.automatic_TradeButton = tkinter.Button(self.tradeFrame, text='Automatic', width=7, height=1, state='disabled', command=self.catch_automatic_button)
        self.automatic_TradeButton.grid(column=1, row=4)

        self.sell_TradeButton = tkinter.Button(self.tradeFrame, text='Sell', width=7, height=1, bg='#F08080',activebackground='#8B0000', state='disabled', command=self.catch_sell_button)
        self.sell_TradeButton.grid(column=5, row=4)

        # Trade Entries
        self.bnbtrade_TradeEntry = tkinter.Entry(self.tradeFrame, width=10, state='disabled')
        self.bnbtrade_TradeEntry.grid(column=1, row=1, ipady=2)

        self.profit_TradeEntry = tkinter.Entry(self.tradeFrame, width=10, state='disabled')
        self.profit_TradeEntry.grid(column=1, row=2, ipady=2)

        self.tokentrade_TradeEntry = tkinter.Entry(self.tradeFrame, width=10, state='disabled')
        self.tokentrade_TradeEntry.grid(column=4, row=1, ipady=2)

        self.pricetrade_TradeEntry = tkinter.Entry(self.tradeFrame, width=10, state='disabled')
        self.pricetrade_TradeEntry.grid(column=4, row=2, ipady=2)

        self.mbamount_TradeEntry = tkinter.Entry(self.tradeFrame, width=10, state='disabled')
        self.mbamount_TradeEntry.grid(column=1, row=3, ipady=2)

        self.gweibuy_TradeEntry = tkinter.Entry(self.tradeFrame, width=10, state='disabled')
        self.gweibuy_TradeEntry.grid(column=3, row=3, ipady=2)

        self.gweisell_TradeEntry = tkinter.Entry(self.tradeFrame, width=10, state='disabled')
        self.gweisell_TradeEntry.grid(column=5, row=3, ipady=2)

        #Checkboxes
        self.allvar1 = tkinter.IntVar()
        self.all_TradeCheckbox = tkinter.Checkbutton(self.tradeFrame, text='100%', state='disabled', variable=self.allvar1, onvalue=1, command=self.check_boxes)
        self.all_TradeCheckbox.grid(column=5, row=1)


        self.profitvar2 = tkinter.IntVar()
        self.profit_TradeCheckbox = tkinter.Checkbutton(self.tradeFrame, state='disabled', text='PROFIT   ', variable=self.profitvar2, onvalue=1, command=self.check_boxes)
        self.profit_TradeCheckbox.grid(column=0, row=2)

        self.keepvar3 = tkinter.IntVar()
        self.keept_TradeCheckbox = tkinter.Checkbutton(self.tradeFrame, state='disabled', text='Keep Tracking %', variable=self.keepvar3, onvalue=1, command=self.catch_keep_markbox)
        self.keept_TradeCheckbox.grid(column=2, row=4, columnspan=2)

        self.maxbuyvar4 = tkinter.IntVar()
        self.maxbuy_TradeCheckbox = tkinter.Checkbutton(self.tradeFrame, text='Maxbuy  ', state='disabled', variable=self.maxbuyvar4, onvalue=1, command=self.check_boxes)
        self.maxbuy_TradeCheckbox.grid(column=0, row=3)


        self.liqvar6 = tkinter.IntVar()
        self.liquidity_TradeCheckbox = tkinter.Checkbutton(self.tradeFrame, text='Liquidity ', state='disabled', variable=self.liqvar6, onvalue=1, command=self.catch_liquidity_markbox)
        self.liquidity_TradeCheckbox.grid(column=0, row=4)

        #Text
        self.text = tkinter.Text(self.tradeFrame, height=3, width=51)
        self.text.insert('insert', "Hello.....")
        self.text.config(state='disabled')
        self.text.grid(column=1, row=6, columnspan=5)
# -------------------------------------------------- FINAL TRADE FRAME FINAL --------------------------------------------------#



        self.taxtext = tkinter.Text(height=5, width=15)
        self.taxtext.insert('insert', "Fee\nBuyTax: ?\nSellTax: ?")
        self.taxtext.config(state='disabled', bg='black', foreground='yellow')
        self.taxtext.grid(column=0, row=4)

        #Calling the function to update hour
        threading.Thread(target=self.gethour).start()

        self.window.mainloop()
# -------------------------------------------------- FUNCTIONS --------------------------------------------------#
            #ALL THE WALLETS AND KEYS ARE STORED AS A LIST OF TUPLES.


    def gethour(self):
        '''This function will maintain the Time updated.'''
        while True:
            timeredeable = dt.datetime.now()
            #Transforming the time in timestamp.
            self.momentTime = dt.datetime.timestamp(timeredeable)
            self.timeredeable = timeredeable.strftime('%H:%M:%S')

            self.hour_label.config(text=self.timeredeable)


    def saveEntry(self):
        '''This function will get and start to analyze the entries.'''
        #Calling the check_is_connected to Analyze.
        self.check_is_connected()

        if self.state == True:
            #updating Window.
            self.status_label.config(text='Connected', fg="green")
            
            

            #Disabling all the User buttons and entries
            self.secretKey_ConnectEntry.config(state='disabled')
            self.tkAddress_ConnectEntry.config(state='disabled')
            self.wtAddress_ConnectEntry.config(state='disabled')
            self.connect_ConnectButton.config(state='disabled')

            #Abling all the Trade Buttons and entries
            self.buy_TradeButton.config(state='normal')
            self.automatic_TradeButton.config(state='normal')
            self.sell_TradeButton.config(state='normal')
            #self.bnbtrade_TradeEntry.config(state='normal')
            #self.bnbtrade_TradeEntry.insert(0, str(self.bnb_in_account[self.wallet_index]))

            #self.profit_entry.config(state='normal')
            self.arrow_TradeButton.config(state='normal')
            self.tokentrade_TradeEntry.config(state='normal')
            self.tokentrade_TradeEntry.config(state='normal')
            self.tokentrade_TradeEntry.insert(0, str(self.token_in_account[self.wallet_index]))
            self.pricetrade_TradeEntry.config(state='normal')
            self.gweibuy_TradeEntry.config(state='normal')
            self.gweisell_TradeEntry.config(state='normal')

            #abling checkboxes
            self.all_TradeCheckbox.config(state='normal')
            self.profit_TradeCheckbox.config(state='normal')
            self.keept_TradeCheckbox.config(state='normal')
            self.maxbuy_TradeCheckbox.config(state='normal')
            self.liquidity_TradeCheckbox.config(state='normal')
            try:
                self.pricetrade_TradeEntry.insert(0, str(self.interaction[0].getTokenPrice()))
            except:
                self.pricetrade_TradeEntry.insert(0, '0000')

    
    #function to interact with listbox cursor.
    def immd(self, e):
        '''Function to make the wallets box interactive'''
        indice = self.listbox_ListboxListbox.curselection()
        try:
            self.wallet_index = int(indice[0])
        except:
            pass
        #Auxiliars function.
        self.openNewWindow(self.wallet_index)
        self.showupwallet(self.wallet_index)

    def openNewWindow(self, index):
        '''Function to open a small window after click in wallet inside walletsBox.'''
        # Toplevel object which will
        if self.newWindow == None:
            self.createwindow(index)
        else:
            self.newWindow.destroy()
            self.newWindow = None
            self.createwindow(index)
    
    def createwindow(self,index):
        '''Function created to be used together with "openNewWindow", here we set the parameters and visual things.'''
        self.newWindow = tkinter.Toplevel(self.window)

        # sets the title of the
        # Toplevel widget
        self.newWindow.title(f'wallet {index}')

        # sets the geometry of toplevel
        self.newWindow.geometry("450x80+500+100")

        # A Label widget to show in toplevel
        tkinter.Label(self.newWindow,
                      text=f"\nAddress: {self.wallets[index][1]}\n\nToken to Buy: {self.wallets[index][2]}").pack()
    
    def addingwallet(self):
        '''Will catch any new wallets to walletsBox, in this part, will not check if the private key is correct.'''
        self.listbox_ListboxListbox.config(state='normal')
        wallet_tuple = self.secretKey_ConnectEntry.get(), self.wtAddress_ConnectEntry.get(), self.tkAddress_ConnectEntry.get()
        self.wallets.append(wallet_tuple)
        self.listbox_ListboxListbox.insert(self.wc_connected,f'{self.wallets[self.wc_connected][1]:.7}')
        self.listbox_ListboxListbox.config(state='disabled')
        self.secretKey_ConnectEntry.delete(0, 'end')
        self.wtAddress_ConnectEntry.delete(0,'end')
        self.wc_connected += 1
        self.wc_ListboxLabel.config(text=f'Wallets {self.wc_connected}')
        self.connect_ConnectButton.config(state="normal")

    def change_text(self, text:str):
        '''Change Text inside the text box.'''
        self.text.config(state='normal')
        self.text.delete('1.0', "end")
        self.text.insert('insert', text)
        self.text.config(state='disabled')
    
    def change_label(self, label:tkinter.Label, text:str):
        '''Change any label of window.'''
        label.config(state='normal')
        label.config(text=text)

    def check_is_connected(self):
        '''This function will check if the private key really belong address, then connect only the correct wallets with all auxiliars class.'''
        wallets_ = 0
        #Filtring all the Entries and connecting only the True wallets/keys
        for _ in range(0, (self.wc_connected)):
            secret_key = self.wallets[wallets_][0]
            wallet_address = self.wallets[wallets_][1]
            token_address = self.wallets[wallets_][2]
            try:
                self.trade.append(Trade(secret_key, wallet_address, token_address))
                try:
                    print(f'Address: {self.trade[wallets_].all_address.my_address}, {self.trade[wallets_].check_Private_key()}')
                    #Connecting on class files.
                    if self.trade[wallets_].check_Private_key() == True:
                        self.interaction.append(GetInteraction(wallet_address, token_address))
                        self.liquidity.append(Monitoring(wallet_address, token_address))
                        #self.taxmonitor.append(Tax(wallet_address, token_address, self.window))
                    else:
                        print('Its not a valid wallet.')
                        self.trade.pop(wallets_)
                        self.listbox_ListboxListbox.config(state='normal')
                        self.listbox_ListboxListbox.delete(wallets_)
                        self.listbox_ListboxListbox.config(state='disabled')
                        self.wallets.remove(self.wallets[wallets_])
                        wallets_ -= 1
                except:
                    print('except')
                    self.trade.pop(wallets_)
                    self.listbox_ListboxListbox.config(state='normal')
                    self.listbox_ListboxListbox.delete(wallets_)
                    self.listbox_ListboxListbox.config(state='disabled')
                    self.wallets.remove(self.wallets[wallets_])
                    wallets_ -= 1

            except ValueError:
                self.listbox_ListboxListbox.config(state='normal')
                self.listbox_ListboxListbox.delete(wallets_)
                self.listbox_ListboxListbox.config(state='disabled')
                self.wallets.remove(self.wallets[wallets_])
                wallets_ -= 1

            wallets_ += 1

        self.listbox_ListboxListbox.config(state='normal')
        self.wc_ListboxLabel.config(text=f'Connected {len(self.trade)}')
        
        for wallet in range(0,len(self.wallets)):
            self.bnb_in_account.append(0)
            self.token_in_account.append(0)

        #putting all the Bnb balances and tokens in a tuple.
        self.updateButtonTrigged()

        #making sure the highest wallet to show up on the initial window.
        for wallet in range(0,len(self.wallets)):
            if self.bnb_in_account[wallet] >= self.testvalue:
                self.showupwallet(wallet)
                self.testvalue = self.bnb_in_account[wallet]
                self.state = True
        return self.state

    def updateButtonTrigged(self):
        if self.wallet_index != 0:
            wallet = self.wallet_index
        print("Caulculando novo saldo")
        '''Will update the balance and show in window after "Update button be clciked" '''
        for wallet in range(0, len(self.wallets)):
            balance = self.interaction[wallet].get_balance()
            bnb = balance[0]
            token = balance[1]
            formatedBNB = f"{bnb:.4f}"
            formatedToken = f"{token:.4f}"
            self.bnb_in_account[wallet] = (float(formatedBNB))
            self.token_in_account[wallet] = float(formatedToken)
            self.showupwallet(wallet)
        print(wallet)


    def showupwallet(self, wallet):
        '''Will change the wallet showed up in Trade Frame for the wallet parsed to function.'''
        self.symbol = self.interaction[wallet].getTokenSymbol()
        self.symboltrade_TradeLabel.config(text=self.symbol)
        self.bnbentry = 0
        self.tokenentry = self.token_in_account[wallet]
        self.title_WalletLabel.config(text=f'wallet {self.wallets[wallet][1]:.7}') #Showing the firsts letters of the address
        self.bnbAmount_WalletLabel.config(text=f'{str(self.bnb_in_account[wallet])} BNB')
        self.tokenAmount_Walletlabel.config(text=f'{str(self.token_in_account[wallet])} {self.symbol}')
        
        #Making sure that entry will be changed with user interaction.
        self.bnbtrade_TradeEntry.config(state='normal')
        self.bnbtrade_TradeEntry.delete(0, 'end')
        self.bnbtrade_TradeEntry.insert(0, str(self.bnb_in_account[wallet]))

    def exchange(self):
        '''This function will update the amount expected exchange between token and busd live value.'''
        bnb_entry = float(self.bnbtrade_TradeEntry.get())
        token_entry = float(self.tokentrade_TradeEntry.get())
        token_actual_price = float(self.interaction[0].getTokenPrice())
        bnb_price = 1 / token_actual_price

        self.pricetrade_TradeEntry.delete(0, 'end')
        self.pricetrade_TradeEntry.insert(0, str(self.interaction[0].getTokenPrice()))

        if bnb_entry != float(self.bnbentry):
            self.bnbentry = bnb_entry
            how_much_token = bnb_entry / token_actual_price
            if how_much_token != 0:
                how_much_token = round(how_much_token, 3) - 0.0001
            self.tokentrade_TradeEntry.delete(0, 'end')
            self.tokentrade_TradeEntry.insert(0, str(how_much_token))
            self.tokenentry = str(how_much_token)

        elif token_entry != float(self.tokenentry):
            self.bnbentry = bnb_entry
            how_much_token2 = token_entry / bnb_price
           
            if how_much_token2 != 0:
                how_much_token2 = round(how_much_token2, 3)-0.0001
            
            self.bnbtrade_TradeEntry.delete(0, 'end')
            
            self.bnbtrade_TradeEntry.insert(0, str(how_much_token))
            self.bnbentry = str(how_much_token2)


    def check_boxes(self):
        '''Just to disable or enable some inputs after a box who owns that input is selected'''
        if self.profitvar2.get() == 1:
            self.profit_TradeEntry.config(state='normal')
        else:
            self.profit_TradeEntry.config(state='disabled')
        
        if self.allvar1.get() == 1:
            self.tokentrade_TradeEntry.config(state='disabled')
        else:
            self.tokentrade_TradeEntry.config(state='normal')

        if self.maxbuyvar4.get() == 1:
            self.mbamount_TradeEntry.config(state='normal')
        else:
            self.mbamount_TradeEntry.config(state='disabled')

        if self.keepvar3.get() == 1:
            self.kept_return = True
        else:
            self.kept_return = False


    def catch_liquidity_markbox(self):
        threading.Thread(target=self.liquidity_mode).start()
    def liquidity_mode(self):
        '''(Only buy if Automate mode is actived.)This function will trigger Liquidity mode, who listen and wait for liquity be added, and stop when user dismark'''
        if self.liqvar6.get() == 1:
            self.liquidity[0].running = True
            if self.liquidity[0].running == True:
                self.liquidity[0].main()
        else:
            self.liquidity[0].breakwhile()
            self.liquidity[0].running = False
            self.liquidity[0].statusreturn = False



    def catch_keep_markbox(self):
        threading.Thread(target=self.keep_mode).start()
    def keep_mode(self):
        '''This function will keep retrieving how much profit you are making.'''
        with open('../token_price_at_trade.txt', 'r') as data:
            token_price = float(data.read())
        while self.keepvar3.get() == 1:
            atual_token = self.interaction[0].getTokenPrice()
            final_profit = ((atual_token * 100) / (token_price * 1)) - 100
            self.change_label(self.profit100_TradeLabel, f'{str(round(final_profit, 2))}%')
        self.change_label(self.profit100_TradeLabel, '%')


    def catch_automatic_button(self):
        '''Using a thread for every single wallet, for all wallets be trigged at the same time'''
        for wallets in range(0, len(self.interaction)):
            GUI.mode_automatic.__defaults__ = (wallets,)
            threading.Thread(target=self.mode_automatic).start()
    def mode_automatic(self, wallet=0):
            '''Able to Buy finnaly, after we select Liquidity option and'''
            maxbuy_entry = self.mbamount_TradeEntry.get()
            bnb_trade_entry = self.bnbtrade_TradeEntry.get()
            profit_entry = self.profit_TradeEntry.get()

            if bnb_trade_entry == '0' or profit_entry == '0':
                bnb_trade_entry = ''
                profit_entry = ''

            try:
                profit = float(profit_entry)
                bnb_tospend = float(bnb_trade_entry)
                old_bnb_tospend = bnb_tospend
            except ValueError:
                messagebox.showerror(title='Error: Automatic Mode', message="Automatic mode needs BNB and Profit entries\n\nPlease, check if you enter number and not letter or leave blank space in BNB or Profit.\n\n(Entries ex.: 0.01 / 0.1 / 1.0 / 1)\n \nVerifique se você preencheu número e não  letra ou deixou espaço em branco em BNB ou Profit")
            else:
                #This if is to make sure that the process will stop or running when User wants. will change the button to Cancel.
                #Elif conditional of this if, will change the button to Connected again and break the running.
                if self.automatic_running == False:
                    self.automatic_TradeButton.config(text='Cancel', bg='#b40d0d', activebackground='#8B0000')
                    self.change_text(f'Listening Transaction for {self.symbol}')
                    self.automatic_running = True
                    self.check_gwei(wallet)

                    while self.automatic_running:
                        if self.liquidity[wallet].statusreturn == True: #and self.taxmonitor[wallet].buytax < 30:
                            if self.maxbuyvar4.get() == 1 and maxbuy_entry != '':
                                bnb_tospend = float(maxbuy_entry) * self.interaction[wallet].getTokenPrice()
                                
                                if bnb_tospend > old_bnb_tospend:
                                    bnb_tospend = old_bnb_tospend

                            self.trade[wallet].buy(bnb_tospend)
                            self.change_text(f'Token was bought\n{self.trade[wallet].buy_contract_address}')
                            print('COMPRADO')
                            self.window.after(100, self.updateButtonTrigged())

                            with open('../token_price_at_trade.txt', 'r') as data:
                                token_price = float(data.read())
                                final_profit = token_price + ((token_price / 100) * profit)

                            while final_profit > self.interaction[0].getTokenPrice():
                                #Return profit in percentage
                                keep_profit = ((self.interaction[wallet].getTokenPrice() * 100) / (token_price * 1)) - 100
                                self.change_label(self.profit100_TradeLabel, str(round(keep_profit, 2)))


                                if float(self.interaction[wallet].getTokenPrice()) > final_profit:
                                    self.trade[wallet].sell(self.token_in_account)
                                    self.window.after(100, self.updateButtonTrigged())
                                    self.change_text(f"Token was Sold\n{self.trade[wallet].sell_contract_address}")
                                    self.automatic_TradeButton.config(text='automatic', bg='#D9D9D9', activebackground='#ECECEC')
                                    self.automatic_running = False
                
                elif self.automatic_running == True:
                    self.automatic_running = False
                    self.liquidity[wallet].breakwhile()
                    self.change_text('')
                    self.automatic_TradeButton.config(text='automatic', bg='#D9D9D9', activebackground='#ECECEC')


    def catch_buy_button(self):
        if self.buy_running == False:
            for wallets in range(0, len(self.interaction)):
                threading.Thread(target=self.mode_buy, args=(wallets,)).start()

        else:
            self.buy_running = False
            self.buy_TradeButton.config(text='Buy', width=7, height=1, bg='#66CDAA', activebackground='#008080')
        

    def mode_buy(self, wallets=0):
        '''WIll only BUY the token address that was connect with the wallet'''
        #Getting the Ui entry.
        bnb_trade_entry = self.bnbtrade_TradeEntry.get()
        profit = self.profit_TradeEntry.get()
        price_entry = self.pricetrade_TradeEntry.get()
        self.change_text('')
        try:
            if bnb_trade_entry == '0' or profit == '0':
                bnb_trade_entry = ''
                profit = ''
                profit = float(profit)
        except ValueError:
            pass
        finally:
            #Elif conditional of this if, will change the button to Connected again and break the running.
                self.buy_running = True
                try:
                    bnb_trade_entry = float(bnb_trade_entry)
                    price_entry = float(price_entry)
                    self.change_text(text=f"{bnb_trade_entry} BNB to get {self.symbol} at {price_entry} profit: {profit}%")

                except ValueError:
                    messagebox.showerror(title='Error: Buy Mode',
                                                 message='Buy mode needs BNB and PRICE/EA entries\n\n(PRICE/EA can be 0 to make the operation with live price)\n\nPlease, check if you enter number and not letter or leave blank space in BNB or PRICE/EA.\n\n(Entries ex.: 0.01 / 0.1 / 1.0 / 1)\n \nVerifique se você preencheu número e não  letra ou deixou espaço em branco em BNB ou PRICE/EA\n\n(PRICE/EA pode ser 0 para fazer a operação com o preço ao vivo)')
                else:
                    self.buy_TradeButton.config(text='Cancel', bg='#b40d0d', activebackground='#8B0000')
                    self.check_gwei(wallets)
                    #Monitoring the Price, If actual price is Lowest than User Buy Price entered, BUY. 
                    while self.buy_running:
                        if float(self.interaction[wallets].getTokenPrice()) <= price_entry:
                            self.trade[wallets].buy(bnb_trade_entry)
                            self.window.after(100, self.updateButtonTrigged())
                            self.change_text(text=f'Token Bought\n{self.trade[wallets].buy_hash}')

                            with open('../token_price_at_trade.txt', 'r') as data:
                                token_price = float(data.read())
                            if profit != '':
                                profit = float(profit)
                                final_profit = token_price + ((token_price / 100) * profit)
                                
                                #Monitoring the Price, If actual price is bigger than User Profit entered, SELL.
                                while self.buy_running:
                                    if float(self.interaction[wallets].getTokenPrice()) >= final_profit:
                                        self.trade[wallets].sell(self.token_in_account)

                                        self.change_text(f'FINALIZED\n{self.trade[wallets].sell_contract_address}')
                                        self.automatic_running = False
                                        self.buy_TradeButton.config(text='Buy', width=7, height=1, bg='#66CDAA',
                                                               activebackground='#008080')
                                       
                                        self.updateButtonTrigged()
                            else:
                                self.buy_running = False
                                self.buy_TradeButton.config(text='Buy', width=7, height=1, bg='#66CDAA',
                                         activebackground='#008080')

            
    def catch_sell_button(self):
        if self.sell_running == False:
            for wallets in range(0, len(self.interaction)):
                threading.Thread(target=self.mode_sell, args=(wallets,)).start()
        else:
            self.sell_running = False
            self.sell_TradeButton.config(text='Sell', width=7, height=1, bg='#F08080', activebackground='#8B0000')

    def mode_sell(self, wallet=0):
        '''WIll only SELL the token address that was connect with the wallet'''
        self.sell_running = True
        self.sell_TradeButton.config(text='Cancel', bg='#b40d0d', activebackground='#8B0000')

        price_entry = self.pricetrade_TradeEntry.get()
        symbol_entry = self.tokentrade_TradeEntry.get()
        
        try:
            if symbol_entry == '0':
                symbol_entry = ''
            symbol_entry = float(symbol_entry)
            price_entry = float(price_entry)
        except ValueError:
            messagebox.showerror(title='Error: Sell Mode', message=f'Buy mode needs {self.symbol} and PRICE/EA entries\n\n(PRICE/EA can be 0 to make the operation with live price)  \n\nPlease, check if you enter number and not letter or leave blank space in {self.symbol} or PRICE/EA.\n\n(Entries ex.: 0.01 / 0.1 / 1.0 / 1)\n \nVerifique se você preencheu número e não  letra ou deixou espaço em branco em {self.symbol} ou PRICE/EA\n\n(PRICE/EA pode ser 0 para fazer a operação com o preço ao vivo)')
        if self.allvar1.get() == 1:
            symbol_entry = True    
        else:
            self.change_text(f'Selling {symbol_entry} {self.symbol} for {price_entry * symbol_entry} BNB')
        
        self.check_gwei(wallet)
        #Monitoring the Price, If actual price is bigger than User Profit entered, SELL.
        while self.sell_running:
                if float(self.interaction[wallet].getTokenPrice()) >= price_entry:
                    if symbol_entry == True:
                        print(self.token_in_account[wallet])
                        
                        print("selling all  amount")
                        balance = self.interaction[wallet].get_balance()
                        bnb = balance[0]
                        token = balance[1]
                        self.trade[wallet].sell(token)
                        
                    else:
                        self.trade[wallet].sell(symbol_entry)

                    self.change_text(f'FINALIZED\n{self.trade[wallet].sell_hash}')
                    self.sell_running = False
                    self.sell_TradeButton.config(text='Sell', width=7, height=1, bg='#F08080',
                                            activebackground='#8B0000')
                    self.window.after(100, self.updateButtonTrigged())
        

    #CHECK GWEI FUNCTION
    def check_gwei(self, wallet):
        '''For Default it will be 9, but user can change at buy time.'''
        gweibuy_entry = self.gweibuy_TradeEntry.get()
        gweisell_entry = self.gweisell_TradeEntry.get()

        if gweibuy_entry != '':
            self.trade[wallet].gweibuy = gweibuy_entry
        else:
            self.trade[wallet].gweibuy = 9
        if gweisell_entry != '':
            self.trade[wallet].gweisell = gweisell_entry
        else:
            self.trade[wallet].gweisell = 9