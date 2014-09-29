# -*- coding: utf-8 -*-
import random
import threading

from django.core.mail import EmailMessage
from django.template import loader, Context

from VideoPair import settings
from core.models import Method, Pair


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_client_ua(request):
    return request.META.get('HTTP_USER_AGENT')


def get_or_none(model, **kwargs):
    objects = model.objects.filter(**kwargs)
    if len(objects) > 0:
        return objects[0]
    else:
        return None


def generate_pairs(number):
    methods = Method.objects.all()
    for _ in xrange(int(number)):
        random2 = random.sample(methods, 2)
        pair = Pair(left=random2[0], right=random2[1])
        pair.save()


class EmailThread(threading.Thread):
    def __init__(self, subject, content, recipient_list):
        self.subject = subject
        self.recipient_list = recipient_list
        self.content = content
        threading.Thread.__init__(self)

    def run(self):
        msg = EmailMessage(self.subject, self.content, settings.EMAIL_HOST_USER, self.recipient_list)
        msg.content_subtype = "html"
        msg.send(fail_silently=False)


def send_email(address=settings.ALERT_EMAIL, template='email/default.html', context=None):
    template = loader.get_template(template)
    EmailThread(u'VideoPair', template.render(Context(context)), [address]).start()
