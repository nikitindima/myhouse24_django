import os
import unicodedata

from django import forms
from django.forms import ModelForm, TextInput, Textarea, CheckboxInput, FileInput

from .models import SiteHomePage, Article, SeoData, SiteAboutPage, GalleryImage, Document


class GalleryImageForm(ModelForm):
    class Meta:
        model = GalleryImage
        fields = ['image']


class DocumentForm(ModelForm):
    name = forms.CharField(required=True, widget=TextInput(attrs={"placeholder": "Введите название документа",
                                                                  "class": "form-control"}))

    class Meta:
        model = Document
        fields = ['name', 'file']
        widgets = {
            "file": FileInput(),
        }

    def clean(self):
        super().clean()
        print('cleaned data', self.cleaned_data)

    def clean_name(self):
        print('clean_name')
        file_name = self.cleaned_data['name']
        print(file_name)
        if file_name:
            print('name is ok')
            file_name = unicodedata.normalize('NFKD', file_name)
            return file_name
        else:
            print('name is None')
            raise forms.ValidationError("Введите корректное имя файла.")

    def clean_file(self):
        print('clean_file')
        uploaded_file = self.cleaned_data['file']
        print(uploaded_file)
        if uploaded_file is None:
            print('file is None')
            raise forms.ValidationError("Загрузите файл.")
        try:
            print(88)
            # check if the file is a valid image
            img = forms.ImageField()
            img.to_python(uploaded_file)
        except forms.ValidationError:
            print(44)
            # file is not a valid image; so check if it's a pdf
            name, ext = os.path.splitext(uploaded_file.name)
            if ext not in ['.pdf', '.PDF']:
                print(55)
                raise forms.ValidationError("Вы можете загружать только изображения и pdf.")
            print(66)
        return uploaded_file


class SiteHomeForm(ModelForm):
    class Meta:
        model = SiteHomePage
        exclude = ["seo_data", "around_us"]
        widgets = {
            "title": TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите заголовок",
                }
            ),
            "description": Textarea(
                attrs={
                    "class": "form-control summernote",
                    "placeholder": "Введите краткий текст",
                }
            ),
            "show_links": CheckboxInput(
                attrs={
                    "class": "",
                }
            ),
            "slider1": FileInput(),
            "slider2": FileInput(),
            "slider3": FileInput(),
        }
        labels = {
            "title": "Заголовок блока",
            "description": "Описание",
            "show_links": "Показать ссылки на приложения",
        }


class SiteAboutForm(ModelForm):
    gallery_upload = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'multiple': True}))
    gallery2_upload = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'multiple': True}))
    documents = forms.FileField(required=False, widget=forms.ClearableFileInput(
        attrs={'multiple': True, 'class': 'upload'}))

    class Meta:
        model = SiteAboutPage
        fields = ["title", "description", "title2", "description2", "portrait"]
        widgets = {
            "title": TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите заголовок",
                }
            ),
            "description": Textarea(
                attrs={
                    "class": "form-control summernote",
                    "placeholder": "Введите краткий текст",
                }
            ),
            "title2": TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите заголовок",
                }
            ),
            "description2": Textarea(
                attrs={
                    "class": "form-control summernote",
                    "placeholder": "Введите краткий текст",
                }
            ),
            "portrait": FileInput(),
        }
        labels = {
            "title": "Заголовок",
            "description": "Краткий текст",
            "title2": "Заголовок",
            "description2": "Краткий текст",
            "portrait": "Фото директора"
        }

    def clean_documents(self):
        uploaded_file = self.cleaned_data['documents']
        try:
            # check if the file is a valid image
            img = forms.ImageField()
            img.to_python(uploaded_file)
        except forms.ValidationError:
            # file is not a valid image; so check if it's a pdf
            name, ext = os.path.splitext(uploaded_file.name)
            if ext not in ['.pdf', '.PDF']:
                raise forms.ValidationError("Вы можете загружать только изображения и pdf.")
        return uploaded_file


class ArticleForm(ModelForm):
    class Meta:
        model = Article
        exclude = []
        widgets = {
            "title": TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите заголовок",
                }
            ),
            "description": Textarea(
                attrs={
                    "class": "form-control summernote",
                    "placeholder": "Введите описание",
                }
            ),
            # 'image': TextInput(attrs={
            #     'class': 'form-control',
            #     'placeholder': 'Введите СЕО ключевые слова',
            # }),
        }

        labels = {
            "title": "Заголовок блока",
            "description": "Описание",
            "image": "Файл",
        }


class SeoDataForm(ModelForm):
    class Meta:
        model = SeoData
        fields = ["title", "description", "keywords"]
        widgets = {
            "title": TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите название для СЕО",
                }
            ),
            "description": Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите СЕО описание",
                    "rows": "6",
                }
            ),
            "keywords": Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите СЕО ключевые слова",
                    "rows": "6",
                }
            ),
        }
        labels = {
            "title": "СЕО - Заголовок",
            "description": "СЕО - Описание",
            "keywords": "СЕО - Ключевые слова",
        }
