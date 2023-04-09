from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        labels = {'text': 'текст постов',
                  'group': 'группа',
                  'image': 'картинка'}
        help_texts = {
            'text': 'текст нового поста',
            'group': 'группа, к которой относится пост',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

