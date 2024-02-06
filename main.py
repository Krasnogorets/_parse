from random import random

import requests, time, json, fake_useragent
from bs4 import BeautifulSoup
import logging


def get_link(text, period):
    ua = fake_useragent.UserAgent()
    data = requests.get(
        url=f"https://hh.ru/search/resume?search_period={period}&order_by=relevance&filter_exp_period=all_time&relocation"
            f"=living_or_relocation&text={text}&gender=unknown&logic=normal&pos=full_text&exp_period=all_time&page=1",
        headers={"user-agent": ua.random}
    )
    if data.status_code != 200:
        return
    soup = BeautifulSoup(data.content, 'lxml')
    try:
        page_count = int(soup.find("div", attrs={'class': 'pager'})
                         .find_all('span', recursive=False)[-1].find('a').find('span').text)
    except Exception as e:
        logging.exception("поймали исключение", e)
        return
    for page in range(page_count):
        try:
            data = requests.get(
                url=f"https://hh.ru/search/resume?search_period={period}&order_by=relevance&filter_exp_period=all_time&relocation"
                    f"=living_or_relocation&text={text}&gender=unknown&logic=normal&pos=full_text&exp_period=all_time&page={page}",
                headers={"user-agent": ua.random}
            )
            if data.status_code != 200:
                continue
            soup = BeautifulSoup(data.content, 'lxml')
            for a in soup.find_all("a", attrs={'class': 'serp-item__title'}):
                yield f"https://hh.ru{a.attrs['href'].split('?')[0]}"
        except Exception as e:
            logging.exception(e)
        time.sleep(1)


def get_cv(link):
    ua = fake_useragent.UserAgent()
    data = requests.get(url=link, headers={"user-agent": ua.random})
    if data.status_code != 200:
        return
    soup = BeautifulSoup(data.content, 'lxml')
    try:
        name = soup.find(attrs={'class': 'resume-block__title-text'}).text
    except Exception as e:
        logging.exception(e)
        name = ""
    try:
        salary = soup.find(attrs={'class': 'resume-block__salary'}).text.replace("\u2009", "").replace("\xa0", " ")
    except Exception as e:
        logging.exception(e)
        salary = ""
    try:
        tags = [tag.text for tag in
                soup.find(attrs={'class': 'bloko-tag-list'}).find_all(attrs={'class': 'skill-name-overflow-auto'})]
    except Exception as e:
        logging.exception(e)
        tags = []
    try:
        experience = soup.find(attrs={'class': 'resume-block__title-text_sub'}).text.replace("\xa0", " ")
    except Exception as e:
        logging.exception(e)
        experience = ""
    try:
        age = soup.find(attrs={'data-qa': 'resume-personal-age'}).text.replace("\xa0", " ")
    except Exception as e:
        logging.exception(e)
        age = ""
    try:
        gender = soup.find(attrs={'data-qa': 'resume-personal-gender'}).text
    except Exception as e:
        logging.exception(e)
        gender = ""
    resume = {"name": name,
              "salary": salary,
              'tags': tags,
              "experience": experience,
              "age": age,
              "gender": gender
              }
    return resume


FORMAT = '{levelname:<8} - {asctime}.' \
         'в строке {lineno} функция "{funcName}()" ' \
         ' выдало сообщение: {msg}'

logging.basicConfig(filename='hh_errors.log',
                    encoding='utf-8', level=logging.ERROR, format=FORMAT, style='{', datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)


def log_all():
    logger.error('Поймали ошибку')
    logger.critical('конец работы')


if __name__ == '__main__':
    log_all()
    POSITION = "Кладовщик"
    PERIOD = 1 # указываем кол-во дней, 1 - за последние сутки, 3, 7, 30, 365
    data = []
    for a in get_link(POSITION, PERIOD):
        data.append(get_cv(a))
        time.sleep(1)
        with open(f'{POSITION}.json', 'w',encoding='utf-8') as f:
            json.dump(data,f,indent=2,ensure_ascii=False)
