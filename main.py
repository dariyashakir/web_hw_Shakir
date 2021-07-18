from tqdm.notebook import tqdm
import requests
from bs4 import BeautifulSoup
import telebot
import random

API_key = '1829703985:AAG3TrFkae7CS23YT0v5cA2lR6Neufj4pwE'

cousine_code = 'adventure'
page_num = 1
url = f'https://mangapoisk.ru/genre/{cousine_code}?page={page_num}'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
# print(soup.prettify())

cousines_html_block = soup.find_all('div', 'row flex-column mx-2')[0]
# print(cousines_html_block)
# print(cousines_html_block.find_all('a'))

cousines = cousines_html_block.find_all('a')
cousine_names = [cousine.text for cousine in cousines]
# print(cousines)
cousine_codes = [cousine['href'] for cousine in cousines]
# print(cousine_codes)

cousine_code_to_name = dict(zip(cousine_codes, cousine_names))
# print(cousine_code_to_name)


manga_names = []
manga_urls = []
manga_images = []
manga_cousine_names = []
MAX_NUM_PAGES = 2
GOOD_RESPONSE_STATUS = 200

for code in tqdm(cousine_codes):
    print(code)
    for page_num1 in range(1, MAX_NUM_PAGES):
        url1 = f'https://mangapoisk.ru{code}?page={page_num1}'
        response1 = requests.get(url1)
        if response1.status_code != GOOD_RESPONSE_STATUS:
            print('err')
            break
        soup1 = BeautifulSoup(response1.content, 'html.parser')
        manga_soups1 = soup1('article', 'flex-item-mini mx-1 splide__slide')
        if len(manga_soups1) == 0:
            print('err')
            break
        for manga_soup1 in manga_soups1:
            name = manga_soup1.a['title']
            print(name)
            m_url = f'https://mangapoisk.ru{manga_soup1.a["href"]}'
            image = manga_soup1.img['data-src']
            manga_names.append(name)
            manga_urls.append(url)
            manga_images.append(image)
            manga_cousine_names.append(
                cousine_code_to_name[code]
            )

"""
ТУТ В ЖУПИТЕРЕ ДАЛЬШЕ ПАНДАТАБЛИЧКА
"""

print("-------------------\nЯ включился...")

botik = telebot.TeleBot(API_key)


@botik.message_handler(commands=['start'])
def send_welcome(message):
    botik.send_message(message.chat.id, f"Привет, {message.from_user.first_name}!\nВводи жанр, а я поищу тебе мангу😘",
                       parse_mode='html')


@botik.message_handler(content_types=['text'])
def echo_all(message):
    mess_text = message.text.strip().lower()
    if mess_text in manga_cousine_names:
        genre_url = list(cousine_code_to_name.keys())[list(cousine_code_to_name.values()).index(mess_text)]
        full_url = f'https://mangapoisk.ru{genre_url}'
        genre_resp = requests.get(full_url)
        if genre_resp.status_code == 200:
            genre_soup = BeautifulSoup(genre_resp.content, 'html.parser')
            teleg_manga_soups = genre_soup('article', 'flex-item-mini mx-1 splide__slide')
            teleg_manga_soup = random.choice(teleg_manga_soups)
            teleg_name = teleg_manga_soup.a['title']
            teleg_m_url = f'https://mangapoisk.ru{teleg_manga_soup.a["href"]}'
            teleg_image = teleg_manga_soup.img['data-src']
        botik.reply_to(message,
                       f"Тааааааак...\nРекомендую тебе почитать {teleg_name}.\n"
                       f"Переходи по ссылочке сюда ✨ {teleg_m_url} ✨.\n"
                       f"Ну а для самых ленивых🥸, можешь решить читать мангу или нет по ее обложке "
                       f"(like a damn sociopath) {teleg_image}")
    else:
        botik.reply_to(message, "Ой, а такого жанра нет😧. Попробуй еще раз, кликнув --> /start")


botik.polling()
