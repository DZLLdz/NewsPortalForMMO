from django import forms
from django.core.exceptions import ValidationError
from ckeditor.widgets import CKEditorWidget
from .models import News, Response


class NewsForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = News
        fields = ['title', 'category', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите заголовок'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Введите текст объявления'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        content = cleaned_data.get('content')
        if content is not None and len(content) < 20:
            raise ValidationError({
                'content': 'Пост не может содержать менее 20 символов'
            })
        if title == content:
            raise ValidationError({
                'title': 'Название поста должно быть отличительным от содержания'
            })

        return cleaned_data


class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['responseType', 'responseMessage',]

    def clean(self):
        cleaned_data = super().clean()
        message = cleaned_data.get('responseMessage')
        type = cleaned_data.get('responseType')
        if type == 'NW':
            raise ValidationError({
                'responseType': 'Измените статус'
            })
        if message is None:
            raise ValidationError({
                'responseMessage': 'Комментарий не должен быть пустым'
            })

        return cleaned_data
