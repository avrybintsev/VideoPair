# -*- coding: utf-8 -*-

from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import render, redirect
from django.template.defaultfilters import register
from VideoPair import settings

from core.forms import AnswerForm, ParticipantForm, PairForm, LoaderForm
from core.models import Pair, Sequence, Method, Participant, Answer, Question
from core.utils import get_client_ip, get_client_ua, get_or_none, generate_pairs, send_email


@register.filter
def average(sum, n):
    return (sum+0.0) / n if n else 0


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
            pairs = Pair.objects.all()

            if len(sequences) > len(pairs):
                generate_pairs(len(sequences) - len(pairs) + 1)
                pairs = Pair.objects.all()
                send_email(template='email/pairs_empty.html')

            pairs = pairs[:len(sequences)]

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
        initial={'best': question.left, 'question': question}) if question else None
    answer_right_form = AnswerForm(
        initial={'best': question.right, 'question': question}) if question else None
    answer_none_form = AnswerForm(
        initial={'best': None, 'question': question} if question else None
    )

    if question is None:
        return redirect(reverse('core.views.index'))

    return render(request, template_name, {
        'video_path': settings.VIDEO_CORE_PATH,
        'participant': participant,
        'counter': {
            'total': total,
            'current': total - len(questions) + 1,
        },
        'question': question,
        'answer_left_form': answer_left_form,
        'answer_right_form': answer_right_form,
        'answer_none_form': answer_none_form,
    })


def invalidate(request):
    del request.session['participant_id']
    return redirect(reverse('core.views.index'))

@staff_member_required
def cp(request, template_name='core/cp.html'):
    if request.method == 'POST':
        pair_form = PairForm(request.POST)

        if pair_form.is_valid():
            pair = pair_form.save(commit=False)
            pair.save()

    methods = Method.objects.all()
    pairs = Pair.objects.all()
    questions = Question.objects.all()
    answers = Answer.objects.all()

    stats = [{
        'method': method,
        'history': questions.filter(Q(left=method) | Q(right=method)).count(),
        'future': pairs.filter(Q(left=method) | Q(right=method)).count(),
    } for method in methods]

    scores = [{
        'method': method,
        'score': sum([answer.get_score(method) for answer in answers]),
        'count': questions.filter(Q(answered=True), Q(left=method) | Q(right=method)).count(),
    } for method in methods]

    return render(request, template_name, {
        'request': request,
        'e_methods_h': list(enumerate(methods)),
        'e_methods_v': list(enumerate(methods)),
        'stats': stats,
        'scores': scores,
    })


@staff_member_required
def loader(request, template_name='core/loader.html'):
    methods = Method.objects.all()
    pairs = Pair.objects.all()
    questions = Question.objects.all()

    proposed_pairs = []

    if request.method == 'POST':
        loader_form = LoaderForm(request.POST)

        if loader_form.is_valid():
            text_pairs = filter(
                lambda x: len(x) == 2,
                map(
                    lambda item: item.split(' '),
                    loader_form.cleaned_data['text'].split('\r\n')
                )
            )

            def get_method(key):
                for method in methods:
                    if method.short_name.upper() == key.upper():
                        return method
                return None

            key_pairs = {
                k: get_method(k) for k in set([item for lst in text_pairs for item in lst])
            }

            proposed_pairs = filter(
                lambda x: x['left'] and x['right'],
                [{'left': key_pairs[item[0]], 'right': key_pairs[item[1]]} for item in text_pairs]
            )

            added_pairs = map(
                lambda x: Pair(left=x['left'], right=x['right']),
                proposed_pairs
            )

            for pair in added_pairs:
                pair.save()

    stats = [{
                 'method': method,
                 'history': questions.filter(Q(left=method) | Q(right=method)).count(),
                 'future': pairs.filter(Q(left=method) | Q(right=method)).count(),
                 } for method in methods]

    loader_form = LoaderForm()

    return render(request, template_name, {
        'loader_form': loader_form,
        'request': request,
        'e_methods_h': list(enumerate(methods)),
        'e_methods_v': list(enumerate(methods)),
        'stats': stats,
        'proposed_pairs': proposed_pairs,
    })


@staff_member_required
def csv(request):
    answers = Answer.objects.all()
    content = '\n'.join([answer.get_string() for answer in answers])
    return HttpResponse(content, content_type='text/csv')


@staff_member_required
def generate(request, number):
    generate_pairs(number)
    return redirect(reverse('core.views.cp'))
