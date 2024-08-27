#  Copyright (c) xxx.xxx.com
#  Author: none

import  logging as log

class TicketInfo:
    def __init__(self, tick_type):
        self.type = tick_type
        self.visitors = []

    def add_visitor(self, visitor):
        log.debug(self.type + " add visitor " + visitor.get_info())
        self.visitors.append(visitor)
        pass

    def get_member_number(self):
        return len(self.visitors)

