# -*- coding: utf-8 -*-
from django.forms import ModelForm, Textarea, TextInput, HiddenInput, Form, CharField

# Extended ModelForm
from core.models import Participant, Answer, Pair


class ExtendedMetaModelForm(ModelForm):
    '''
    Allow the setting of any field attributes via the Meta class.
    '''
    def __init__(self, *args, **kwargs):
        '''
        Iterate over fields, set attributes from Meta.field_args.
        '''
        super(ExtendedMetaModelForm, self).__init__(*args, **kwargs)
        if hasattr(self.Meta, 'field_args'):
            # Look at the field_args Meta class attribute to get
            # any (additional) attributes we should set for a field.
            field_args = self.Meta.field_args
            # Iterate over all fields...
            self.items = self.fields.items()
            for fname, field in self.items:
                # Check if we have something for that field in field_args
                fargs = field_args.get(fname)
                if fargs:
                    # Iterate over all attributes for a field that we
                    # have specified in field_args
                    for attr_name, attr_val in fargs.items():
                        if attr_name.startswith('+'):
                            merge_attempt = True
                            attr_name = attr_name[1:]
                        else:
                            merge_attempt = False
                        orig_attr_val = getattr(field, attr_name, None)
                        if orig_attr_val and merge_attempt and \
                                    type(orig_attr_val) == dict and \
                                    type(attr_val) == dict:
                            # Merge dictionaries together
                            orig_attr_val.update(attr_val)
                        else:
                            # Replace existing attribute
                            setattr(field, attr_name, attr_val)


class ParticipantForm(ExtendedMetaModelForm):
    class Meta:
        model = Participant
        fields = ('name', 'email')

        field_args = {
            'name' : {
                'widget' : TextInput(attrs={'class':''}),
                'error_messages':  {'required' : u'Необходимое поле', 'invalid': u'Некоректный формат данных'},
                'required': True,
            },
            'email' : {
                'widget' : TextInput(attrs={'class':''}),
                'error_messages':  {'required' : u'Необходимое поле', 'invalid': u'Некоректный формат данных'},
            },
        }


class AnswerForm(ExtendedMetaModelForm):
    class Meta:
        model = Answer
        fields = ('best', 'question')

        field_args = {
            'best': {
                'widget': HiddenInput(),
            },
            'question': {
                'widget': HiddenInput(),
            }
        }


class PairForm(ExtendedMetaModelForm):
    class Meta:
        model = Pair
        fields = ('left', 'right')


class LoaderForm(Form):
    text = CharField()
