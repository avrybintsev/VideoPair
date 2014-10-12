# -*- coding: utf-8 -*-

from django.db import models


class Sequence(models.Model):
    TYPE_CHOICE = ((0, None), (1, 'girls'), (2, 'creatures'),)

    sequence_type = models.SmallIntegerField(choices=TYPE_CHOICE, default=0, verbose_name=u'Тип')
    name = models.CharField(max_length=200, verbose_name=u'Название')

    class Meta:
        verbose_name = u'Sequence'
        verbose_name_plural = u'Sequences'

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def __unicode__(self):
        return unicode(self.name)


class Method(models.Model):
    full_name = models.CharField(max_length=200, verbose_name=u'Полное название')
    middle_name = models.CharField(max_length=200, blank=True, verbose_name=u'Название')
    short_name = models.CharField(max_length=200, blank=True, verbose_name=u'Короткое название')
    year = models.IntegerField(blank=True, verbose_name=u'Год')
    notes = models.TextField(blank=True, verbose_name=u'Примечания')

    class Meta:
        verbose_name = u'Method'
        verbose_name_plural = u'Methods'

    def __repr__(self):
        return self.short_name

    def __str__(self):
        return self.short_name

    def __unicode__(self):
        return unicode(self.short_name)


class Pair(models.Model):
    left = models.ForeignKey(Method, related_name='pair_left_method', verbose_name=u'Первый метод')
    right = models.ForeignKey(Method, related_name='pair_right_method', verbose_name=u'Второй метод')

    class Meta:
        verbose_name = u'Pair'
        verbose_name_plural = u'Pairs'

    def __repr__(self):
        return '{} vs {}'.format(self.left, self.right)

    def __str__(self):
        return '{} vs {}'.format(self.left, self.right)

    def __unicode__(self):
        return unicode(u'{} vs {}'.format(self.left, self.right))


class Participant(models.Model):
    name = models.CharField(max_length=200, verbose_name=u'Имя')
    email = models.EmailField(max_length=200, blank=True, verbose_name=u'EMail')
    date = models.DateTimeField(auto_now_add=True, verbose_name=u'Дата')
    ip = models.CharField(max_length=16, verbose_name=u'IP address')
    ua = models.TextField(verbose_name=u'User-Agent')

    class Meta:
        verbose_name = u'Participant'
        verbose_name_plural = u'Participants'

    format_date = lambda obj: obj.date.strftime('%d.%b.%Y %H:%M')
    format_date.short_description = u'Дата'
    format_date.admin_order_field = 'date'

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def __unicode__(self):
        return unicode(self.name)


class Question(models.Model):
    left = models.ForeignKey(Method, related_name='question_left_method', verbose_name=u'Первый метод')
    right = models.ForeignKey(Method, related_name='question_right_method', verbose_name=u'Второй метод')
    sequence = models.ForeignKey(Sequence, verbose_name=u'Последовательность')
    participant = models.ForeignKey(Participant, verbose_name=u'Участник')
    answered = models.BooleanField(verbose_name=u'Есть ответ')

    class Meta:
        verbose_name = u'Question'
        verbose_name_plural = u'Questions'

    def has_method(self, method):
        return self.right == method or self.left == method

    def __repr__(self):
        return '{} vs {} [{}] <{}>'.format(self.left, self.right, self.sequence, self.participant)

    def __str__(self):
        return '{} vs {} [{}] <{}>'.format(self.left, self.right, self.sequence, self.participant)

    def __unicode__(self):
        return unicode(u'{} vs {} [{}] <{}>'.format(self.left, self.right, self.sequence, self.participant))


class Answer(models.Model):
    date = models.DateTimeField(auto_now_add=True, verbose_name=u'Дата')
    question = models.ForeignKey(Question, verbose_name=u'Вопрос')
    best = models.ForeignKey(Method, blank=True, null=True, related_name='best_method', verbose_name=u'Лучший')

    class Meta:
        verbose_name = u'Answer'
        verbose_name_plural = u'Answers'

    def get_worst(self):
        if self.best is None:
            return None
        if self.question.left == self.best:
            return self.question.right
        return self.question.left

    def get_letter(self):
        if self.best == self.question.left:
            return 'F'
        elif self.best == self.question.right:
            return 'S'
        return 'N'

    def get_score(self, method):
        if self.best == method:
            return 1
        elif self.best is None and self.question.has_method(method):
            return 0.5
        return 0

    def get_string(self):
        return u'{},{},{},{},{}'.format(
            self.question.sequence.name,
            self.question.left.short_name,
            self.question.right.short_name,
            self.get_letter(),
            self.question.participant.email
        )

    format_date = lambda obj: obj.date.strftime('%d.%b.%Y %H:%M')
    format_date.short_description = u'Дата'
    format_date.admin_order_field = 'date'

    question_left = lambda obj: obj.question.left
    question_left.short_description = u'Первый метод'

    question_right = lambda obj: obj.question.right
    question_right.short_description = u'Второй метод'

    question_sequence = lambda obj: obj.question.sequence
    question_sequence.short_description = u'Последовательность'

    question_participant = lambda obj: obj.question.participant
    question_participant.short_description = u'Участник'

    def __repr__(self):
        return '{}! {}'.format(self.best, self.question)

    def __str__(self):
        return '{}! {}'.format(self.best, self.question)

    def __unicode__(self):
        return unicode(u'{}! {}'.format(self.best, self.question))
