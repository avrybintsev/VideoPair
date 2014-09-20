# -*- coding: utf-8 -*-

from django.db import models


class Sequence(models.Model):
    TYPE_CHOICE = ((0, None), (1, 'girls'), (2, 'creatures'),)

    sequence_type = models.SmallIntegerField(choices=TYPE_CHOICE, default=0, verbose_name=u'Тип')
    name = models.CharField(max_length=200, verbose_name=u'Название')

    def __repr__(self):
        return self.name

    def __unicode__(self):
        return unicode(self.name)


class Method(models.Model):
    full_name = models.CharField(max_length=200, verbose_name=u'Полное название')
    middle_name = models.CharField(max_length=200, blank=True, verbose_name=u'Название')
    short_name = models.CharField(max_length=200, blank=True, verbose_name=u'Короткое название')
    year = models.IntegerField(blank=True, verbose_name=u'Год')
    notes = models.TextField(blank=True, verbose_name=u'Примечания')

    def __repr__(self):
        return self.short_name

    def __unicode__(self):
        return unicode(self.short_name)


class Pair(models.Model):
    left = models.ForeignKey(Method, related_name='left_method', verbose_name=u'Первый метод')
    right = models.ForeignKey(Method, related_name='right_method', verbose_name=u'Второй метод')
    sequence = models.ForeignKey(Sequence, verbose_name=u'Последовательность')

    def __repr__(self):
        return '{} vs {} [{}]'.format(self.left, self.right, self.sequence)

    def __unicode__(self):
        return unicode(u'{} vs {} [{}]'.format(self.left, self.right, self.sequence))


class Participant(models.Model):
    name = models.CharField(max_length=200, verbose_name=u'Имя')
    email = models.EmailField(max_length=200, verbose_name=u'EMail')
    ip = models.CharField(max_length=16, verbose_name=u'IP address')
    ua = models.TextField(verbose_name=u'User-Agent')

    def __repr__(self):
        return self.name

    def __unicode__(self):
        return unicode(self.name)


class Answer(models.Model):
    participant = models.ForeignKey(Participant, verbose_name=u'Участник')
    date = models.DateTimeField(verbose_name=u'Дата')
    sequence = models.ForeignKey(Sequence, verbose_name=u'Последовательность')
    better = models.ForeignKey(Method, related_name='better_method', verbose_name=u'Лучший')
    worse = models.ForeignKey(Method, related_name='worse_method', verbose_name=u'Худший')

    def __repr__(self):
        return '{} > {} [{}] [{}]'.format(self.better, self.worse, self.sequence, self.participant)

    def __unicode__(self):
        return unicode(u'{} > {} [{}] [{}]'.format(self.better, self.worse, self.sequence, self.participant))
