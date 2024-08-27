#  Copyright (c) xxx.xxx.com
#  Author: none

import logging as log
from time import sleep

import ddddocr
import xlrd
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from auto_tickets.ticket_info import TicketInfo
from auto_tickets.visitor_info import VisitorInfo


class BuyTickets:
    old_man_ticket = '老年人票'
    adult_team_ticket = '成人团队票'
    child_team_free_ticket = '团队未成年人免费票'
    element_wait_time = 600

    def __init__(self):
        self.browser = None

        self.account = '18519366011'
        self.password = 'tu654321@'
        self.file_path = '/Users/shanks/Desktop/抢票名单.xls'

        self.old_man_order = TicketInfo(BuyTickets.old_man_ticket)
        self.adult_team_order = TicketInfo(BuyTickets.adult_team_ticket)
        self.child_team_order = TicketInfo(BuyTickets.child_team_free_ticket)

    def buy(self):
        self.load_orders()
        if not self.has_order():
            log.info('no need buy ticket')
            return
        self.login()
        self.prepare_query()
        self.query()

    def prepare_query(self):
        self.browser.find_element(By.XPATH,
                                  '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/ul/li/span').click()
        self.browser.find_element(By.XPATH,
                                  '/html/body/div[1]/div/div[1]/div[2]/div[1]/div[1]/div[2]/ul/li[1]/div/span').click()
        pass

    def login(self):
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(BuyTickets.element_wait_time)
        self.browser.maximize_window()

        self.browser.get("https://usermg.dpm.org.cn/usercenter/login")
        self.browser.find_element(By.XPATH,
                                  '//*[@id="app"]/div/div[2]/div/div/div[3]/div/form/div[1]/div/div[1]/input').send_keys(
            self.account)
        # sleep(1) # wait for the password input box
        self.browser.find_element(By.XPATH,
                                  '//*[@id="app"]/div/div[2]/div/div/div[3]/div/form/div[2]/div/div[1]/input').send_keys(
            self.password)
        verify_code_img = self.browser.find_element(By.XPATH,
                                                    '//*[@id="app"]/div/div[2]/div/div/div[3]/div/form/div[3]/div/div/img')
        verify_code_img.screenshot('verify_code_img.png')
        ocr = ddddocr.DdddOcr()
        with open('verify_code_img.png', 'rb') as f:
            img_bytes = f.read()
        res = ocr.classification(img_bytes)
        self.browser.find_element(By.XPATH,
                                  '//*[@id="app"]/div/div[2]/div/div/div[3]/div/form/div[3]/div/div[1]/div/input').send_keys(
            res)
        self.browser.find_element(By.XPATH, '//*[@id="app"]/div/div[2]/div/div/div[3]/div/form/button').click()
        pass

    def load_orders(self):
        workbook = xlrd.open_workbook(self.file_path)
        sheet = workbook.sheets()[0]
        rows = sheet.nrows
        cols = sheet.ncols
        if rows < 2 or cols < 4:
            log.info("invalid workbook row:" + rows + " col: " + cols)
            return
        for row in range(1, rows):
            type_value = str(sheet.cell(row, 0).value).strip()
            name_value = str(sheet.cell(row, 1).value).strip()
            id_card_type = str(sheet.cell(row, 2).value).strip()
            id_value = str(sheet.cell(row, 3).value).strip()
            visitor = VisitorInfo(name_value, id_card_type, id_value)
            if type_value == BuyTickets.old_man_ticket:
                self.old_man_order.add_visitor(visitor)
            elif type_value == BuyTickets.adult_team_ticket:
                self.adult_team_order.add_visitor(visitor)
            elif type_value == BuyTickets.child_team_free_ticket:
                self.child_team_order.add_visitor(visitor)
            else:
                log.info("invalid ticket type " + type_value)
        pass

    def has_order(self):
        old_men_order_number = self.old_man_order.get_member_number()
        adult_number_order_number = self.adult_team_order.get_member_number()
        child_number_order_number = self.child_team_order.get_member_number()
        total = old_men_order_number + adult_number_order_number + child_number_order_number
        log.debug(
            "old_men_order_number:" + str(old_men_order_number) + " adult_number_order_number:" + str(
                adult_number_order_number) + " child_number_order_number:" + str(
                child_number_order_number) + " total:" + str(total))
        return total > 0

    def query(self):
        got_ticket = False
        current_day = 0
        day_element_list = [
            '/html/body/div[1]/div/div[1]/div[2]/div[2]/div[2]/div/div/div/div/div/div/div/div/div/div/div[1]/div/div[1]/div/form/div[1]/div/div/div[1]/span[2]',
            '/html/body/div[1]/div/div[1]/div[2]/div[2]/div[2]/div/div/div/div/div/div/div/div/div/div/div[1]/div/div[1]/div/form/div[1]/div/div/div[2]/span[2]'
        ]

        while not got_ticket:
            self.browser.find_element(By.XPATH, day_element_list[current_day]).click()
            for time_line in range(0, 2):
                if self.query_ticket(time_line):
                    return
            current_day += 1
            if current_day >= len(day_element_list):
                sleep(50)
                current_day = 0
        pass

    def query_ticket(self, time_line):
        got_old_man_ticket = self.query_old_man_ticket(time_line)
        got_adult_team_ticket = self.query_adult_team_ticket(time_line)
        got_child_team_ticket = self.query_child_team_ticket(time_line)
        return got_old_man_ticket and got_adult_team_ticket and got_child_team_ticket

    def query_old_man_ticket(self, time_line):
        if self.old_man_order.get_member_number() == 0:
            return True
        order_count_element = '/html/body/div[1]/div/div[1]/div[2]/div[2]/div[2]/div/div/div/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div[4]/div[2]/table/tbody/tr[1]/td[1]/div/div/div/div/input'
        if not self.is_element_present(order_count_element):
            return False
        if time_line == 0:
            ##self.browser.find_element(By.XPATH, order_count_element).clear()
            self.browser.find_element(By.XPATH, order_count_element).send_keys(str(self.old_man_order.get_member_number()))
        self.browser.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[2]/div[2]/div/div/div/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div[4]/div[1]/table/thead/tr/th[1]').click()
        time_element = None

        if time_line == 0:
            forenoon_element = '/html/body/div[1]/div/div[1]/div[2]/div[2]/div[2]/div/div/div/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div[2]/table/tbody/tr[2]/td/div/div/div/div/div[1]/div/span'
            if not self.is_element_present(forenoon_element):
                return False
            time_element = self.browser.find_elements(By.XPATH, forenoon_element)
        else:
            afternoon_element =  '/html/body/div[1]/div/div[1]/div[2]/div[2]/div[2]/div/div/div/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div[2]/table/tbody/tr[2]/td/div/div/div/div/div[2]/div/span'
            if not self.is_element_present(afternoon_element):
                return False
            time_element = self.browser.find_elements(By.XPATH, afternoon_element)

        if not time_element.is_selected():
            time_element.click()
        return True

    def is_element_present(self, path_info):
        self.browser.implicitly_wait(1)
        element = self.browser.find_elements(By.XPATH, path_info)
        self.browser.implicitly_wait(BuyTickets.element_wait_time)
        return len(element) > 0

    def query_adult_team_ticket(self, time_line):
        if self.adult_team_order.get_member_number() == 0:
            return True
        order_count_element = '/html/body/div[1]/div/div[1]/div[2]/div[2]/div[2]/div/div/div/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div[4]/div[2]/table/tbody/tr[4]/td[1]/div/div/div/div/input'
        if not self.is_element_present(order_count_element):
            return False
        if time_line == 0:
            ##self.browser.find_element(By.XPATH, order_count_element).clear()
            self.browser.find_element(By.XPATH, order_count_element).send_keys(str(self.adult_team_order.get_member_number()))
        self.browser.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[2]/div[2]/div/div/div/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div[4]/div[1]/table/thead/tr/th[1]').click()
        time_element = None

        if time_line == 0:
            forenoon_element = '/html/body/div[1]/div/div[1]/div[2]/div[2]/div[2]/div/div/div/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div[2]/table/tbody/tr[4]/td/div/div/div/div/div[1]/div/span'
            if not self.is_element_present(forenoon_element):
                return False
            time_element = self.browser.find_elements(By.XPATH, forenoon_element)
        else:
            afternoon_element = '/html/body/div[1]/div/div[1]/div[2]/div[2]/div[2]/div/div/div/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div[2]/table/tbody/tr[4]/td/div/div/div/div/div[2]/div/span'
            if not self.is_element_present(afternoon_element):
                return False
            time_element = self.browser.find_elements(By.XPATH, afternoon_element)

        if not time_element.is_selected():
            print("select false")
            time_element.click()
        return True

    def query_child_team_ticket(self, time_line):
        if self.child_team_order.get_member_number() == 0:
            return True
        order_count_element = '/html/body/div[1]/div/div[1]/div[2]/div[2]/div[2]/div/div/div/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div[4]/div[2]/table/tbody/tr[6]/td[1]/div/div/div/div/input'
        if not self.is_element_present(order_count_element):
            return False
        if time_line == 0:
            ##self.browser.find_element(By.XPATH, order_count_element).clear()
            self.browser.find_element(By.XPATH, order_count_element).send_keys(str(self.child_team_order.get_member_number()))
        self.browser.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[2]/div[2]/div/div/div/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div[4]/div[1]/table/thead/tr/th[1]').click()
        print(self.child_team_order.get_member_number())
        time_element = None

        if time_line == 0:
            forenoon_element = '/html/body/div[1]/div/div[1]/div[2]/div[2]/div[2]/div/div/div/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div[2]/table/tbody/tr[6]/td/div/div/div/div/div[1]/div/span'
            if not self.is_element_present(forenoon_element):
                return False
            time_element = self.browser.find_elements(By.XPATH, forenoon_element)
        else:
            afternoon_element = '/html/body/div[1]/div/div[1]/div[2]/div[2]/div[2]/div/div/div/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div[2]/table/tbody/tr[6]/td/div/div/div/div/div[2]/div/span'
            if not self.is_element_present(afternoon_element):
                return False
            time_element = self.browser.find_elements(By.XPATH, afternoon_element)

        if not time_element.is_selected():
            print("select false")
            time_element.click()
        return True


