import json
import os

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
import time


from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait



class Controller:

    def __init__(self, login_input):
        self.login = login_input
        self.dictionary = load_dict('!databases/' + self.login + '.json')
        self.driver = webdriver.Chrome()

    def wait_for(self, xpath, timeout=15):
        try:
            WebDriverWait(self.driver, timeout).until(expected_conditions.presence_of_element_located((By.XPATH, xpath)))
        except TimeoutException:
            print(f'time limit exceeded for waiting on {xpath}')
            export(self.dictionary, '!databases/' + self.login + '.json')
            quit()

    def click(self, xpath):
        self.wait_for(xpath)
        self.driver.find_element(By.XPATH, xpath).click()
        time.sleep(0.5)

    def get_text(self, xpath):
        self.wait_for(xpath)
        return self.driver.find_element(By.XPATH, xpath).text

    def send_keys(self, xpath, text):
        self.wait_for(xpath)
        self.driver.find_element(By.XPATH, xpath).send_keys(text)

    def logon(self, login, passwd):
        self.driver.get('https://lingos.pl/home/login')
        self.send_keys('/html/body/div[1]/div[2]/div/div/form/div[1]/input', login)   # type login into login field
        self.send_keys('/html/body/div[1]/div[2]/div/div/form/div[2]/input', passwd)  # type password into password field
        self.click('/html/body/div[1]/div[2]/div/div/form/div[3]/button')                   # click login button
        time.sleep(1.5)

    def do_lesson(self, times):
        for i in range(times):
            # start lesson
            self.click('/html/body/div[3]/div/div[2]/div/div/div[1]/div/div[2]/a')  # click learn button

            # type words into field until the lesson ends
            while not self.driver.current_url.startswith('https://lingos.pl/students/group'):

                time.sleep(0.5)

                # if there is a new word, add it to dictionary
                if self.get_text('/html/body/div[2]/div/div/div/div/div/h5[1]/span') == 'NOWE SŁOWO!':  # check if there is a new word to be added
                    translation = self.get_text('/html/body/div[2]/div/div/div/div/div/h3[1]')
                    polish_word = self.get_text('/html/body/div[2]/div/div/div/div/div/h3[2]')
                    self.dictionary[polish_word] = translation
                    self.click('/html/body/div[2]/div/div/div/div/div/div/button')  # click next

                else:
                    polish_word = self.get_text('/html/body/div[2]/div/div/div/div/div/h3')
                    next_btn = '/html/body/div[2]/div/div/div/div/div/div[4]/button'

                    # get the word from dict and type it into input field, then click next
                    if polish_word in self.dictionary:
                        translated = self.dictionary[polish_word]
                        self.send_keys('/html/body/div[2]/div/div/div/div/div/div[2]/input', translated)  # input translater word into answer field
                        self.click(next_btn)
                        self.click(next_btn)

                    # doesn't know the word so click next to get the correct word, save it and click next
                    else:
                        self.click(next_btn)
                        translation = self.get_text('//*[@id="flashcard_error_correct"]')  # get answer
                        self.dictionary[polish_word] = translation
                        self.click(next_btn)

            # add 1 to daily_lessons in user file
            data = load_dict('!users/' + self.login + '.json')
            data['lessons_today'] += 1
            export(data, '!users/' + self.login + '.json')

            if self.driver.current_url == 'https://lingos.pl/students/group/finished':
                self.driver.get('https://lingos.pl/students/group')

        self.driver.close()


def export(data, file):
    export_file = open(file, 'w')
    json.dump(data, export_file, indent=4)
    export_file.close()


def load_dict(file) -> dict:
    # checks if data.json file exists
    # if yes imports it as data / if no creates data dict
    if os.path.exists(file):
        json_file = open(file, 'r')
        data = json.load(json_file)
        json_file.close()
    else:
        data = {}
    return data
