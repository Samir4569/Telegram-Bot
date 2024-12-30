import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup

def fetch_news():
    chrome_options = Options()
    service = Service('C:/Users/Samir/Downloads/130.0.6723.58 chromedriver-win64/chromedriver-win64/chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get('https://www.bbc.com/')
    driver.implicitly_wait(10)

    soup = BeautifulSoup(driver.page_source, 'lxml')
    divs = soup.find_all('div', {'data-testid': 'anchor-inner-wrapper'})

    data = []
    for div in divs:
        heading_tag = div.find('h1') or div.find('h2') or div.find('h3') 
        heading = heading_tag.text.strip() if heading_tag else None

        p_tag = div.find('p', {'data-testid': 'card-description'})
        description = p_tag.text.strip() if p_tag else None

        a_tag = div.find('a', {'data-testid': 'internal-link'})
        link = a_tag.get('href') if a_tag else None

        if link and not link.startswith('https://'):
            link = 'https://www.bbc.com' + link

        data.append({
            'Heading': heading,
            'Description': description,
            'Link': link
        })

    driver.quit()

    df = pd.DataFrame(data)
    df = df.dropna(subset=['Heading', 'Link', 'Description'])
    df = df.drop_duplicates()
    return df

def send_message_to_telegram(bot_token, chat_id, message):
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }
    response = requests.post(url, data=payload)
    return response.json()

def fetch_and_send_news():
    df = fetch_news()

    bot_token = '7994228781:AAEqWp0HoYU9QuC_Ygeu8rFxHqnp3Us7au8'
    chat_id = '1909975784'

    for _, row in df.iterrows():
        message = f"**{row['Heading']}**\n\n_{row['Description']}_\n\n{row['Link']}"
        send_message_to_telegram(bot_token, chat_id, message)

if __name__ == "__main__":
    try:
        fetch_and_send_news()
    except Exception as e:
        print(f"An error occurred: {e}")
