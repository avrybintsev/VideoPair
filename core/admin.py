from django.contrib import admin
from core.models import Sequence, Method, Pair, Participant, Answer, Question


class AnswerAdmin(admin.ModelAdmin):
    list_display = ('best', 'question_left', 'question_right', 'question_sequence', 'question_participant', 'format_date')


class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'format_date', 'ip')


class MethodAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'short_name')


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('left', 'right', 'sequence', 'participant', 'answered')


class SequenceAdmin(admin.ModelAdmin):
    list_display = ('name', 'sequence_type')


class PairAdmin(admin.ModelAdmin):
    list_display = ('left', 'right')


admin.site.register(Sequence, SequenceAdmin)
admin.site.register(Method, MethodAdmin)
admin.site.register(Pair, PairAdmin)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)

