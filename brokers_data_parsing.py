import random
import fake_useragent
from seleniumbase.common.exceptions import NoSuchElementException, ElementNotVisibleException, TimeoutException
from selenium.webdriver.common.by import By
from seleniumbase import SB
import time
import json

base_URL = 'https://www.yatco.com/broker-finder/?sort=1&pagination=1&total_result_count=1' \
           '&page_index=1&page_size=12&records=12&getforsalestats=1&has_been_processed=true'

useragent = fake_useragent.UserAgent()
with SB(uc=True, headless=True, headless2=True, incognito=True, agent=useragent.random, block_images=True) as sb:
    for i in range(138, 142):
        page = i
        data = {}
        URL = f'https://www.yatco.com/broker-finder/?sort=1&pagination=1&total_result_count=1' \
              f'&page_index={page}&page_size=12&records=12&getforsalestats=1&has_been_processed=true'
        starting_time = time.time()

        sb.open(URL)

        ending_time = time.time()
        print(ending_time - starting_time)
        starting_time = time.time()
        list_brokers_names = sb.find_elements('a.card-title')
        list_brokers_names2 = sb.find_elements('div.card-title')
        list_links = sb.find_elements("DETAILS", by=By.LINK_TEXT)

        count = 1
        for el in list_brokers_names:
            data[f"id_{count}"] = {"name": el.text,
                                   "Address": None, "Listing": None, "LOA_range": None,
                                   "Price_range": None, 'Phone#1': None, 'Phone#2': None,
                                   'br_link': None,
                                   'Company': None}
            count += 1
        count = 1
        count_names = 1
        for el in list_brokers_names2:
            if count % 2 != 0:
                data[f"id_{count_names}"]["Address"] = el.text.split('\n')[0]
            if count % 2 == 0:
                data[f"id_{count_names}"]["Listing"] = el.text.split('\n')[0].split(":")[1]
                data[f"id_{count_names}"]["LOA_range"] = el.text.split('\n')[1].split(":")[1]
                data[f"id_{count_names}"]["Price_range"] = el.text.split('\n')[2].split(":")[1]
                count_names += 1

            count += 1
        count = 1
        for el in list_links:
            data[f"id_{count}"]["br_link"] = el.get_attribute('href')
            print(el.get_attribute('href'))
            with SB(uc=True, headless=True, incognito=True, agent=useragent.random) as sb1:
                sb1.open(el.get_attribute('href'))
                try:
                    sb1.click('//*[@id="site-content"]/div[1]/div/div/div[1]/div/'
                              'div/div/div/div/div/div[4]/a[1]', delay=0)
                except NoSuchElementException as e:
                    print(e)
                try:
                    data[f"id_{count}"]["Phone#1"] = \
                        sb1.find_element('//*[@id="single-broker-modal-call"]/div[2]/a/button').text
                except NoSuchElementException as e:
                    print(e)
                    data[f"id_{count}"]["Phone#1"] = "none"
                try:
                    data[f"id_{count}"]["Phone#2"] = \
                        sb1.find_element('//*[@id="single-broker-modal-call"]/div[3]/a/button').text
                except NoSuchElementException as e:
                    print(e)
                    data[f"id_{count}"]["Phone#2"] = ""
                try:
                    data[f"id_{count}"]["Company"] = \
                        sb1.find_element('//*[@id="single-broker-modal-call"]/div[1]/div/h5[2]').text
                except Exception as e:
                    print(e)
                    try:
                        data[f"id_{count}"]["Company"] = \
                            sb1.find_element('//*[@id="single-broker-modal-email"]/div/div/h5[2]').text
                    except NoSuchElementException as e:
                        print(e)
            count += 1

        with open(f'data/page_{page}.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        ending_time = time.time()
        print(ending_time - starting_time)
