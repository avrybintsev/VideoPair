# -*- coding: utf-8 -*-
import datetime
import random
from collections import namedtuple
from django.contrib.admin.views.decorators import staff_member_required

from django.core.urlresolvers import reverse
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render, redirect

from core.forms import AnswerForm, ParticipantForm
from core.models import Pair, Sequence, Method
from core.utils import get_client_ip, get_client_ua


Question = namedtuple('Question', ('sequence', 'left', 'right', 'answered'))

def index(request, template_name='core/index.html'):

    participant = request.session.get('participant')
    questions = request.session.get('questions')

    if request.method == 'POST':
        participant_form = ParticipantForm(request.POST)

        if participant_form.is_valid():
            participant = participant_form.save(commit=False)
            participant.ip = get_client_ip(request),
            participant.ua = get_client_ua(request),
            participant.date = datetime.datetime.now(),
            participant.save()

            sequences = Sequence.objects.all()
            pairs = Pair.objects.all()[:len(sequences)]
            questions = [Question(sequence, pair.left, pair.right, False) for sequence, pair in zip(sequences, pairs)]
            pairs.delete()

            request.session['participant'] = participant
            request.session['questions'] = questions

            return redirect(reverse('ask'))
        else:
            return HttpResponseBadRequest()



    return render(request, template_name, {
        'participant': participant,
        'questions': questions,
    })


def ask(request, template_name='core/ask.html'):
    participant = request.session.get('participant')
    questions = request.session.get('questions')

    answered = len(filter(lambda x: x.answered, questions))
    question = (x for x in questions if not x.answered).next()

    if not (participant and questions):
        return HttpResponseForbidden()

    if request.method == 'POST':
        answer_form = AnswerForm(request.POST)

        if answer_form.is_valid():
            answer = answer_form.save(commit=False)
            answer.date = datetime.datetime.now()
            answer.participant = participant
            answer.save()

            question.answered = True

    return render(request, template_name, {
        'participant': participant,
        'questions': questions,
        'answered': answered,
        'question': question,
    })


@staff_member_required
def arp(request):
    methods = Method.objects.all()
    sequences = Sequence.objects.all()
    for _ in xrange(len(sequences)):
        random2 = random.sample(methods, 2)
        pair = Pair(left=random2[0], right=random2[1])
        pair.save()
    return redirect(reverse('index'))