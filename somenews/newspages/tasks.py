import datetime
import os
import time

import json
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from celery import shared_task
from .models import News, Response, Subscription


@shared_task
def send_last_weak_post():
    today = datetime.datetime.now()
    last_week = today - datetime.timedelta(days=7)
    categories = News.TYPENEWS
    for cat in categories:
        newss = News.objects.filter(publicationDate__gte=last_week, category=cat).all()
        subs = Subscription.objects.filter(category=cat).all()
        subscribers = []
        subscribers += [sub.user.email for sub in subs]
        html_content = render_to_string(
            'mail_messages_weeksend.html',
            {
                'link': os.getenv("SITE_URL"),
                'newss': newss,
            }
        )
        msg = EmailMultiAlternatives(
            subject=f'MMO_Portal weeksend for {cat}',
            body='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=subscribers,
        )
        msg.attach_alternative(html_content, 'text/html')
        msg.send()


def send_mail_comment(pk, category, title, content, subs):
    html_content = render_to_string(
        'protect/mail_message_comment.html',
        {
            'title': title,
            'content': content,
            'category': category,
            'link': f'{os.getenv("SITE_URL")}/{"news"}/{pk}'
        }
    )

    msg = EmailMultiAlternatives(
        subject=f'NEW Comment for NEWS: {title}',
        body='',
        from_email=os.getenv("DEFAULT_FROM_EMAIL"),
        to=[f'{subs}'],
    )
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


def send_mail_new_post(pk, category, title, content, subs):
    html_content = render_to_string(
        'protect/mail_message_news_add.html',
        {
            'title': title,
            'content': content,
            'category': category,
            'link': f'{os.getenv("SITE_URL")}/{"news"}/{pk}'
        }
    )

    msg = EmailMultiAlternatives(
        subject=f'NEW NEWS: {title}',
        body='',
        from_email=os.getenv("DEFAULT_FROM_EMAIL"),
        to=subs,
    )
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


def send_mail_react(pk, category, title, content, subs):
    html_content = render_to_string(
        'protect/mail_message_react.html',
        {
            'title': title,
            'content': content,
            'category': category,
            'link': f'{os.getenv("SITE_URL")}/{"news"}/{pk}'
        }
    )

    msg = EmailMultiAlternatives(
        subject=f'NEW NEWS: {title}',
        body='',
        from_email=os.getenv("DEFAULT_FROM_EMAIL"),
        to=[f'{subs}'],
    )
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


@shared_task
def notify_about_new_post(json_str):
    json_str_to_json = json.loads(json_str)
    time.sleep(3)
    subscribers = Subscription.objects.filter(category=json_str_to_json['category']).all()
    subscribers_emails = []
    subscribers_emails += [adr.user.email for adr in subscribers]
    send_mail_new_post(json_str_to_json["id"],
                       json_str_to_json["category"],
                       json_str_to_json["title"],
                       json_str_to_json["content"],
                       subscribers_emails)


@shared_task
def notify_about_comment(json_str, email, title):
    json_str_to_json = json.loads(json_str)
    time.sleep(3)
    send_mail_comment(json_str_to_json["responseNews_id"],
                      json_str_to_json["responseType"],
                      title,
                      json_str_to_json["responseMessage"],
                      email)


@shared_task
def notify_about_react(json_str, email, title, status_reaction):
    json_str_to_json = json.loads(json_str)
    time.sleep(3)
    send_mail_react(json_str_to_json["responseNews_id"], status_reaction,
                    title, json_str_to_json["responseMessage"], email)

