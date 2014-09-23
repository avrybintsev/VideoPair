# -*- coding: utf-8 -*-
import datetime
import random
from collections import namedtuple

from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render, redirect

from core.forms import AnswerForm, ParticipantForm, PairForm
from core.models import Pair, Sequence, Method, Participant, Answer, Question
from core.utils import get_client_ip, get_client_ua, get_or_none


def index(request, template_name='core/index.html'):
    participant_id = request.session.get('participant_id')
    participant = get_or_none(Participant, pk=participant_id)

    if request.method == 'POST':
        participant_form = ParticipantForm(request.POST)

        if participant_form.is_valid():
            participant = participant_form.save(commit=False)
            participant.ip = get_client_ip(request),
            participant.ua = get_client_ua(request),
            participant.save()

            sequences = Sequence.objects.all()
            pairs = Pair.objects.all()[:len(sequences)]

            for sequence, pair in zip(sequences, pairs):
                question = Question(
                    participant=participant,
                    left=pair.left,
                    right=pair.right,
                    sequence=sequence,
                    answered=False
                )
                question.save()
                pair.delete()

            request.session['participant_id'] = participant.id

            return redirect(reverse('core.views.ask'))

    questions = Question.objects.filter(participant=participant, answered=False)
    if questions:
        return redirect('core.views.ask')

    participant_form = ParticipantForm()

    return render(request, template_name, {
        'participant': participant,
        'participant_form': participant_form,
    })


def ask(request, template_name='core/ask.html'):
    participant_id = request.session.get('participant_id')
    participant = get_or_none(Participant, pk=participant_id)

    if not participant:
        return HttpResponseForbidden()

    if request.method == 'POST':
        answer_form = AnswerForm(request.POST)

        if answer_form.is_valid():
            answer = answer_form.save(commit=False)
            answer.save()

            answer.question.answered = True
            answer.question.save()

            return redirect(reverse('core.views.ask'))

    total = Sequence.objects.all().count()
    questions = Question.objects.filter(participant=participant, answered=False)
    question = questions[0] if questions else None

    answer_left_form = AnswerForm(
        initial={'better': question.left, 'worse': question.right, 'question': question}) if question else None
    answer_right_form = AnswerForm(
        initial={'better': question.right, 'worse': question.left, 'question': question}) if question else None

    if question is None:
        return redirect(reverse('core.views.index'))

    return render(request, template_name, {
        'participant': participant,
        'counter': {
            'total': total,
            'current': total - len(questions) + 1,
        },
        'question': question,
        'answer_left_form': answer_left_form,
        'answer_right_form': answer_right_form,
    })


@staff_member_required
def cp(request, template_name='core/cp.html'):
    sequences = Sequence.objects.all()
    methods = Method.objects.all()
    pairs = Pair.objects.all()
    questions = Question.objects.all()
    answers = Answer.objects.all()
    participants = Participant.objects.all()

    stats = [{
        'method': method,
        'history': questions.filter(Q(left=method) | Q(right=method)).count(),
        'future': pairs.filter(Q(left=method) | Q(right=method)).count(),
    } for method in methods]

    best = [{
        'method': method,
        'votes': answers.filter(better=method).count(),
    } for method in methods]

    if request.method == 'POST':
        pair_form = PairForm(request.POST)

        if pair_form.is_valid():
            pair = pair_form.save(commit=False)
            # check for left != right ?
            pair.save()

    return render(request, template_name, {
        'sequences': sequences,
        'methods': methods,
        'pairs': pairs,
        'questions': questions,
        'answers': answers,
        'participants': participants,
        'stats': stats,
        'best': best,
    })


@staff_member_required
def generate(request, number):
    methods = Method.objects.all()
    for _ in xrange(int(number)):
        random2 = random.sample(methods, 2)
        pair = Pair(left=random2[0], right=random2[1])
        pair.save()
    return redirect(reverse('core.views.index'))