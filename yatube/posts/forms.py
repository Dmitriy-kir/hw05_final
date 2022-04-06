from django import forms

from .models import Post,Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст поста',
            'group': 'Группа',
            'image': 'Картинка заметки'
        }


    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['group'].empty_label = 'Выберите группу'

    def clean_text(self):
        text = self.cleaned_data['text']
        if text == 'Толстой - графоман!':
            raise forms.ValidationError(
                'Эй! Ты просто его плохо знаешь!'
            )
        return text


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text',]

    def clean_subject(self):
        text = self.cleaned_data['text']
        if text == '':
            raise forms.ValidationError(
                'Вы должны обязательно что-то написать',
                params={'text': text},
            )
        return text