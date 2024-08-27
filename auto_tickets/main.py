#  Copyright (c) xxx.xxx.com
#  Author: none
from time import sleep

from buy_tickets import BuyTickets
import logging as log

if __name__ == '__main__':
    log.basicConfig(filename="running.log", level=log.DEBUG, filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    log.debug("start buy tickets")
    buy_tickets = BuyTickets()
    buy_tickets.buy()