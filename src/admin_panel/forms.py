from django.forms import ModelForm, TextInput, Textarea, CheckboxInput, FileInput

from .models import SiteHomePage, Article, SeoData


class SiteHomeForm(ModelForm):
    class Meta:
        model = SiteHomePage
        exclude = ['seo_data', 'around_us']
        widgets = {
            'title': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите заголовок',
            }),
            'description': Textarea(attrs={
                'class': 'form-control summernote',
                'placeholder': 'Введите краткий текст',
            }),
            'show_links': CheckboxInput(attrs={
                'class': '',
            }),
            'slider1': FileInput(),
            'slider2': FileInput(),
            'slider3': FileInput(),
        }
        labels = {
            'title': 'Заголовок блока',
            'description': 'Описание',
            'show_links': 'Показать ссылки на приложения',
        }


class ArticleForm(ModelForm):
    class Meta:
        model = Article
        exclude = []
        widgets = {
            'title': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите заголовок',
            }),
            'description': Textarea(attrs={
                'class': 'form-control summernote',
                'placeholder': 'Введите описание',
            }),
            # 'image': TextInput(attrs={
            #     'class': 'form-control',
            #     'placeholder': 'Введите СЕО ключевые слова',
            # }),
        }

        labels = {
            'title': 'Заголовок блока',
            'description': 'Описание',
            'image': 'Файл',
        }


class SeoDataForm(ModelForm):
    class Meta:
        model = SeoData
        fields = ['title', 'description', 'keywords']
        widgets = {
            'title': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название для СЕО',
            }),
            'description': Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Введите СЕО описание',
                'rows': '6'
            }),
            'keywords': Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Введите СЕО ключевые слова',
                'rows': '6'
            }),
        }
        labels = {
            'title': 'СЕО - Заголовок',
            'description': 'СЕО - Описание',
            'keywords': 'СЕО - Ключевые слова',
        }
