#  Copyright (c) xxx.xxx.com
#  Author: none

class VisitorInfo:
    def __init__(self, name, id_card_type, id_number):
        self.name = name
        self.id_card_type = id_card_type
        self.id_number = id_number

    def get_name(self):
        return self.name

    def get_id(self):
        return self.id_number

    def get_info(self):
        return "name " + self.name + " id card " + self.id_card_type + " number " + self.id_number