import os
import sys
import django
import datetime
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import get_user_model

# Run Django
project = os.path.dirname(os.path.abspath('manage.py'))
sys.path.append(project)
os.environ['DJANGO_SETTINGS_MODULE'] = 'scraping_srv.settings'
django.setup()

from scraping.models import *
from scraping_srv.settings import EMAIL_HOST_USER

EMAIL_ADMIN_USER = EMAIL_HOST_USER

today = datetime.date.today()
subject = f'Рассылка вакансий за {today}'
text_content = f'Рассылка вакансий {today}'
from_email = EMAIL_HOST_USER

empty = '<h2>К сожалению а сегодня по Вашим предпочтениям данных нет.</h2>'

User = get_user_model()
users = User.objects.filter(send_email=True).values('city', 'language', 'email')
users_dict = {}
for user in users:
    users_dict.setdefault((user['city'], user['language']), [])
    users_dict[(user['city'], user['language'])].append(user['email'])
if users_dict:
    params = {
        'city_id__in': [],
        'language_id__in': [],
    }
    for city, language in users_dict.keys():
        params['city_id__in'].append(city)
        params['language_id__in'].append(language)
    vacancies = Vacancy.objects.filter(**params, timestamp=today).values()
    vacancies_dict = {}
    for vacancy in vacancies:
        vacancies_dict.setdefault((vacancy['city_id'], vacancy['language_id']), [])
        vacancies_dict[(vacancy['city_id'], vacancy['language_id'])].append(vacancy)
    for keys, emails in users_dict.items():
        rows = vacancies_dict.get(keys, [])
        html = ''
        for row in rows:
            html += f'<div><a href="{row["url"]}">{row["title"]}</a></div>'
            html += f'<p>{row["description"]}</p>'
            html += f'<p>{row["company"]}</p><br /><hr>'
        html_ = html if html else empty
        for email in emails:
            to = email
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_, "text/html")
            msg.send()

qs = Error.objects.fileter(timestamp=today)
if qs.exists():
    error = qs.first()
    data = error.data
    content = ''
    for i in data:
        html_ += f'<p><a href="{i["url"]}">Error: {i["title"]}</a></p>'
    subject = 'Ошибки скрапинга'
    text_content = 'Ошибки скрапинга'
    to = EMAIL_ADMIN_USER
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_, "text/html")
    msg.send()