import requests
from bs4 import BeautifulSoup
from telegram import Bot
import asyncio
import time

# إعدادات البوت
TELEGRAM_TOKEN = '7833348608:AAEfqRaK9m6DZEO7cv5kirWlAIh_iwTXeiQ'
CHANNEL_ID = '@datascience_courses'
bot = Bot(token=TELEGRAM_TOKEN)

# اسم الملف لتخزين الكورسات المرسلة
SENT_COURSES_FILE = 'sent_courses.txt'

async def send_message_async(message):
    await bot.send_message(chat_id=CHANNEL_ID, text=message)

def get_discounted_courses():
    url = 'https://www.udemy.com/courses/search/?q=data%20science&discount=on'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    courses = []
    for course in soup.find_all('div', class_='course-card--content--all'):
        title = course.find('h3').get_text(strip=True)
        link = course.find('a')['href']  # جلب رابط الكورس
        discount_price = course.find('span', class_='price--discount').get_text(strip=True) if course.find('span', class_='price--discount') else None
        
        if discount_price and title:
            courses.append((title, link))
    
    return courses

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
    # إرسال رسالة اختبار عند بدء تشغيل البوت
    await send_message_async("البوت يعمل بشكل صحيح!")

    while True:
        try:
            discounted_courses = get_discounted_courses()
            if discounted_courses:
                await send_courses_to_channel(discounted_courses)
        except Exception as e:
            print(f'Error: {e}')
        await asyncio.sleep(10)  # انتظر 10 ثواني قبل التحقق مرة أخرى

async def send_courses_to_channel(courses):
    for title, link in courses:
        if not has_sent_course(title):
            message = f'[{title}](https://www.udemy.com{link})'  # صياغة الرسالة كرابط
            await send_message_async(message)
            save_sent_course(title)

# بدء التشغيل
if __name__ == "__main__":
    asyncio.run(main())
