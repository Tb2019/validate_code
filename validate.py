# -*- coding: utf-8 -*-
import string
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import requests
from hashlib import md5

class Chaojiying_Client(object):

    def __init__(self, username, password, soft_id):
        self.username = username
        password =  password.encode('utf8')
        self.password = md5(password).hexdigest()
        self.soft_id = soft_id
        self.base_params = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
        }

    def PostPic(self, im, codetype):
        """
        im: 图片字节
        codetype: 题目类型 参考 http://www.chaojiying.com/price.html
        """
        params = {
            'codetype': codetype,
        }
        params.update(self.base_params)
        files = {'userfile': ('ccc.jpg', im)}
        r = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params, files=files, headers=self.headers)
        return r.json()

    def PostPic_base64(self, base64_str, codetype):
        """
        im: 图片字节
        codetype: 题目类型 参考 http://www.chaojiying.com/price.html
        """
        params = {
            'codetype': codetype,
            'file_base64':base64_str
        }
        params.update(self.base_params)
        r = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params, headers=self.headers)
        return r.json()

    def ReportError(self, im_id):
        """
        im_id:报错题目的图片ID
        """
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://upload.chaojiying.net/Upload/ReportError.php', data=params, headers=self.headers)
        return r.json()


class Validate:
    def __init__(self, ori_code_list):
        self.url = 'https://t66y.com/register.php'
        self.ori_code_list = ori_code_list
        self.options =webdriver.ChromeOptions()
        self.options.add_experimental_option('detach', True)

        self.service = Service('D:/Software/anaconda/envs/spider/chromedriver.exe')

        self.chaojiying = Chaojiying_Client('982148620', 'w3150201126', '954644')

        self.num = list(range(0, 10))
        self.letters = list(string.ascii_lowercase)

    def gen_code(self):
        for code in self.ori_code_list:
            # for num in self.num:
            #     code_ = code + str(num)
            #     yield code_
            for letter in self.letters:
                code_ = code + letter
                yield code_

    def get_validation_code(self):
        self.driver.find_element(By.XPATH, '//a[contains(text(), "點擊顯示")]').click()
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//img[@id="codeImg"]')))
        img_ele = self.driver.find_element(By.XPATH, '//img[@id="codeImg"]')
        time.sleep(1)
        img_ele.screenshot(r'C:\Users\98214\Desktop\a.png')
        im = open(r'C:\Users\98214\Desktop\a.png', 'rb').read()
        res = self.chaojiying.PostPic(im, 1004)
        val_code = res['pic_str']
        img_code = res['pic_id']
        return val_code, img_code

    def check(self, val_int_ele, code_input_ele):
        validation_code = self.get_validation_code()
        val_int_ele.send_keys(validation_code[0])
        self.driver.find_element(By.XPATH, '//input[contains(@value, "檢查邀請碼")]').click()
        WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, '//div[@id="check_info_invcode"]/span')))
        if '邀請碼不存在' in self.driver.find_element(By.XPATH, '//div[@id="check_info_invcode"]/span').text:
            code_input_ele.clear()
            return 'continue'
        elif '驗證碼不正確' in self.driver.find_element(By.XPATH, '//div[@id="check_info_invcode"]/span').text:
            self.chaojiying.ReportError(validation_code[1])
            return self.check()

            # # 重复操作
            # validation_code = self.get_validation_code()
            # val_int_ele.send_keys(validation_code[0])
            # self.driver.find_element(By.XPATH, '//input[contains(@value, "檢查邀請碼")]').click()
            # WebDriverWait(self.driver, 5).until(
            #     EC.presence_of_element_located((By.XPATH, '//div[@id="check_info_invcode"]/span')))
            # if '邀請碼不存在' in self.driver.find_element(By.XPATH, '//div[@id="check_info_invcode"]/span').text:
            #     code_input_ele.clear()
            #     continue
            # if '驗證碼不正確' in self.driver.find_element(By.XPATH, '//div[@id="check_info_invcode"]/span').text:
            #     self.chaojiying.ReportError(validation_code[1])
            #     a = input('验证码解析错误，手动输入验证码后继续，验证完输入1继续程序')
            #     if a == '1':
            #         code_input_ele.clear()
            #         continue
        else:
            # print('邀请码已经找到：', code)
            return 'success'



    def auto_validate_code(self):
        self.driver = webdriver.Chrome(options=self.options, service=self.service)
        self.driver.get(self.url)

        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//input[@name="regsubmit"]')))
        code_input_ele = self.driver.find_element(By.XPATH, '//input[@id="invcode"]')
        val_int_ele = self.driver.find_element(By.XPATH, '//input[@id="validate"]')

        codes = self.gen_code()
        for code in codes:
            code_input_ele.send_keys(code)
            res = self.check(val_int_ele, code_input_ele)
            if res == 'continue':
                continue
            elif res == 'success':
                print('邀请码已经找到：', code)
                break
        self.driver.close()



if __name__ == '__main__':
    v = Validate(['d3d3f7515c063af'])
    v.auto_validate_code()
