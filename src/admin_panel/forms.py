import os
import unicodedata
from collections import OrderedDict

from django import forms
from django.forms import ModelForm, TextInput, Textarea, CheckboxInput, FileInput
from django.forms.widgets import URLInput, EmailInput, NumberInput, Select
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _
from django_form_builder.forms import BaseDynamicForm
from django_form_builder import dynamic_fields

from .models import (
    SiteHomePage,
    Article,
    SeoData,
    SiteAboutPage,
    GalleryImage,
    Document,
    SiteContactsPage,
    House,
    Section,
    Floor,
    Flat,
)

# 2.5MB - 2621440
# 5MB - 5242880
# 10MB - 10485760
# 20MB - 20971520
# 50MB - 5242880
# 100MB 104857600
# 250MB - 214958080
# 500MB - 429916160
from .services.forms_services import check_filesize, validate_image

MAX_UPLOAD_SIZE = 20971520


# region SHARED_STAFF
class GalleryImageForm(ModelForm):
    class Meta:
        model = GalleryImage
        fields = ["image"]


# endregion SHARED_STAFF

# region SITE_CONTROL


class DocumentForm(ModelForm):
    name = forms.CharField(
        required=True,
        widget=TextInput(
            attrs={"placeholder": "Введите название документа", "class": "form-control"}
        ),
    )

    class Meta:
        model = Document
        fields = ["name", "file"]
        widgets = {
            "file": FileInput(),
        }

    def clean_name(self):
        print("clean_name")
        file_name = self.cleaned_data["name"]
        print(file_name)
        if file_name:
            print("name is ok")
            file_name = unicodedata.normalize("NFKD", file_name)
            return file_name
        else:
            print("name is None")
            raise forms.ValidationError("Введите корректное имя файла.")

    def clean_file(self):
        uploaded_file = self.cleaned_data["file"]

        check_filesize(uploaded_file, MAX_UPLOAD_SIZE)

        if uploaded_file is None:
            raise forms.ValidationError("Загрузите файл.")
        try:
            # check if the file is a valid image
            img = forms.ImageField()
            img.to_python(uploaded_file)
        except forms.ValidationError:
            # file is not a valid image; so check if it's a pdf
            name, ext = os.path.splitext(uploaded_file.name)
            if ext not in [".pdf", ".PDF"]:
                print(55)
                raise forms.ValidationError(
                    "Вы можете загружать только изображения и pdf."
                )

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
                    "placeholder": "Введите описание",
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
    gallery_upload = forms.ImageField(
        required=False, widget=forms.ClearableFileInput(attrs={"multiple": True})
    )
    gallery2_upload = forms.ImageField(
        required=False, widget=forms.ClearableFileInput(attrs={"multiple": True})
    )
    documents = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={"multiple": True, "class": "upload"}),
    )

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
            "portrait": "Фото директора",
        }

    def clean_documents(self):
        uploaded_file = self.cleaned_data["documents"]
        try:
            # check if the file is a valid image
            img = forms.ImageField()
            img.to_python(uploaded_file)
        except forms.ValidationError:
            # file is not a valid image; so check if it's a pdf
            name, ext = os.path.splitext(uploaded_file.name)
            if ext not in [".pdf", ".PDF"]:
                raise forms.ValidationError(
                    "Вы можете загружать только изображения и pdf."
                )
        return uploaded_file


class SiteContactsForm(ModelForm):
    class Meta:
        model = SiteContactsPage
        exclude = [
            "seo_data",
        ]
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
            "website": URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите ссылку на сайт",
                }
            ),
            "name": TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите имя контатного лица",
                }
            ),
            "phone": TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите телефон контатного лица",
                }
            ),
            "map": Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите код гугл карты",
                    "rows": "6",
                }
            ),
            "email": EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите адрес электронной почты",
                }
            ),
            "location": TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите локацию (улица, дом)",
                }
            ),
            "address": TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите адрес (район, город)",
                }
            ),
        }


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
                }
            ),
            # "description": SummernoteWidget(
            #     attrs={
            #         'summernote': {'disableResizeEditor': 'true', 'height': '200', 'width': '100%',
            #                        'placeholder': 'введите описание'}
            #     }
            # ),
        }

        labels = {
            "title": "Заголовок блока",
            "description": "Описание",
            "image": "Файл",
        }

    def clean_title(self):
        article_title = self.cleaned_data["title"]
        if article_title:
            article_title = unicodedata.normalize("NFKD", article_title)
            return article_title
        else:
            raise forms.ValidationError("Введите заголовок статьи.")

    def clean_description(self):
        article_description = self.cleaned_data["description"]
        if article_description:
            article_description = unicodedata.normalize("NFKD", article_description)
            return article_description
        else:
            raise forms.ValidationError("Введите описание.")

    def clean_file(self):
        uploaded_file = self.cleaned_data["image"]

        if uploaded_file is None:
            raise forms.ValidationError("Загрузите файл.")

        check_filesize(uploaded_file, MAX_UPLOAD_SIZE)

        try:
            # check if the file is a valid image
            img = forms.ImageField()
            img.to_python(uploaded_file)
        except forms.ValidationError:
            raise forms.ValidationError("Вы можете загружать только изображения.")

        return uploaded_file


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


# endregion SITE_CONTROL

# region PROPERTY
# region staff
class SectionForm(ModelForm):
    class Meta:
        model = Section
        fields = ["name", "floors"]
        widgets = {
            "name": TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите название секции",
                }
            ),
            "floors": NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите количество этажей",
                    "type": "number",
                    "max": 500,
                    "min": 5,
                }
            ),
        }
        labels = {
            "name": "Название",
            "floors": "Этажи",
        }


class FloorForm(forms.ModelForm):
    class Meta:
        model = Floor
        fields = ["name"]
        widgets = {
            "name": TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите название этажа",
                }
            ),
        }
        labels = {"name": "Название"}


# endregion staff


class HouseForm(ModelForm):
    class Meta:
        model = House
        fields = ["name", "address", "image1", "image2", "image3", "image4", "image5"]

        widgets = {
            "name": TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите название дома",
                }
            ),
            "address": TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите адрес дома",
                }
            ),
            "image1": FileInput(),
            "image2": FileInput(),
            "image3": FileInput(),
            "image4": FileInput(),
            "image5": FileInput(),
        }
        labels = {
            "name": "Название",
            "address": "Адрес",
            "image1": "Изображение #1. Размер: (522x350)",
            "image2": "Изображение #2. Размер: (248x160)",
            "image3": "Изображение #3. Размер: (248x160)",
            "image4": "Изображение #4. Размер: (248x160)",
            "image5": "Изображение #5. Размер: (248x160)",
        }

    def clean(self):
        cleaned_data = super().clean()
        for image in ["image1", "image2", "image3", "image4", "image5"]:
            validate_image(self, image, max_size=MAX_UPLOAD_SIZE)
        return cleaned_data


class HouseUpdateForm(HouseForm):
    class Meta(HouseForm.Meta):
        model = House


class HouseCreateForm(HouseForm):
    class Meta(HouseForm.Meta):
        model = House


# region FLAT
class FlatForm(ModelForm):
    # floor = forms.ChoiceField(widget=forms.Select, choices=[(x, str(x)) for x in range(10)])

    class Meta:
        model = Flat
        fields = [
            "number",
            "area",
            "floor",
            "section",
            "house",
            "owner",
            "account",
            "tariff",
        ]
        widgets = {
            "number": TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите номер квартиры",
                }
            ),
            "area": NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите номер квартиры",
                }
            ),
            "section": Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите номер квартиры",
                }
            ),
            "floor": Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите этаж",
                },
                choices=[(0, "---------")],
            ),
            "house": Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите номер квартиры",
                }
            ),
            "owner": Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Выберите владельца",
                }
            ),
            "account": Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите номер квартиры",
                }
            ),
            "tariff": Select(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите номер квартиры",
                }
            ),
        }
        labels = {
            "number": "Номер квартиры",
            "area": "Площадь квартиры",
            "floor": "Этаж",
            "section": "Секция",
            "house": "Дом",
            "owner": "Владелец",
            "account": "Лицевой счет",
            "tariff": "Тариф",
        }


class FlatCreateForm(FlatForm):
    class Meta(FlatForm.Meta):
        model = Flat


class FlatUpdateForm(FlatForm):
    class Meta(FlatForm.Meta):
        model = Flat


# endregion FLAT
# endregion PROPERTY
