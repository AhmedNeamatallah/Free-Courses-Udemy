import os
import requests
from bs4 import BeautifulSoup
from telegram import Bot
import asyncio
import logging
from main import TELEGRAM_TOKEN, CHANNEL_ID  # استيراد المتغيرات من main.py

# إعدادات التسجيل
logging.basicConfig(level=logging.INFO)

# إعدادات البوت
bot = Bot(token=TELEGRAM_TOKEN)

# اسم الملف لتخزين الكورسات المرسلة
SENT_COURSES_FILE = 'sent_courses.txt'

async def send_message_async(message):
    try:
        await bot.send_message(chat_id=CHANNEL_ID, text=message)
        logging.info("Message sent: %s", message)
    except Exception as e:
        logging.error("Failed to send message: %s", e)

def get_discounted_courses():
    try:
        url = 'https://www.udemy.com/courses/search/?q=data%20science&discount=on'
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
        soup = BeautifulSoup(response.content, 'html.parser')

        courses = []
        for course in soup.find_all('div', class_='course-card--content--all'):
            title = course.find('h3').get_text(strip=True)
            link = course.find('a')['href']
            discount_price = course.find('span', class_='price--discount')

            if discount_price and title:
                courses.append((title, link))
        
        return courses
    except Exception as e:
        logging.error("Error fetching courses: %s", e)
        return []

def has_sent_course(title):
    try:
        with open(SENT_COURSES_FILE, 'r') as f:
            sent_courses = f.read().splitlines()
        return title in sent_courses
    except FileNotFoundError:
        return False

def save_sent_course(title):
    with open(SENT_COURSES_FILE, 'a') as f:
        f.write(title + '\n')

async def main():
    await send_message_async("البوت يعمل بشكل صحيح!")
    while True:
        discounted_courses = get_discounted_courses()
        if discounted_courses:
            await send_courses_to_channel(discounted_courses)
        await asyncio.sleep(1200)  # الانتظار ساعة20 دقيقة قبل التحقق مرة أخرى

async def send_courses_to_channel(courses):
    for title, link in courses:
        if not has_sent_course(title):
            message = f'[{title}](https://www.udemy.com{link})'
            await send_message_async(message)
            save_sent_course(title)

if __name__ == "__main__":
    asyncio.run(main())
