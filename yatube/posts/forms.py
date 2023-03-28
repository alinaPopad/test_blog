from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group']
        labels = {'text': 'текст постов', 'group': 'группа'}
        help_texts = {
            'text': 'текст нового поста',
            'group': 'группа, к которой относится пост',
        }
