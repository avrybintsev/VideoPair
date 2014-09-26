# -*- coding: utf-8 -*-
import random
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