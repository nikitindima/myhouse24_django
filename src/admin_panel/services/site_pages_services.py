from django.forms import modelformset_factory
from django.http import QueryDict

from src.admin_panel.forms import (
    ArticleForm,
    SiteHomeForm,
    SeoDataForm,
    GalleryImageForm,
    DocumentForm,
)
from src.admin_panel.models import (
    SiteHomePage,
    SeoData,
    Article,
    GalleryImage,
    Document, SiteServicesPage,
)


def get_or_create_page_object(obj_model):
    obj = obj_model.objects.last()
    if obj is None:
        seo_data = SeoData()
        seo_data.save()
        obj = obj_model(seo_data=seo_data)
        obj.save()

    if obj_model is SiteHomePage:
        articles_count = 6
        while obj.around_us.all().count() < articles_count:
            article = Article()
            article.save()
            obj.around_us.add(article)

    return obj


def create_formset(request, obj_m2m_field, formset_type):
    if formset_type is Article:
        formset_factory = modelformset_factory(
            Article, form=ArticleForm, fields=["title", "description", "image"], extra=0, can_delete=True
        )
        formset = formset_factory(
            request.POST or None,
            request.FILES or None,
            prefix="formset_article",
            queryset=obj_m2m_field.all(),
        )
        return formset

    elif formset_type is Document:
        formset_factory = modelformset_factory(
            Document, form=DocumentForm, fields=["name", "file"], extra=0
        )
        formset = formset_factory(
            request.POST or None,
            request.FILES or None,
            prefix="formset_document",
            queryset=obj_m2m_field.all(),
        )
        return formset

    else:
        raise Exception("Wrong formset type passed in func create_formset")


def create_gallery_formset(obj_field, request):
    formset_factory = modelformset_factory(
        GalleryImage, form=GalleryImageForm, fields=["image"], extra=0
    )
    formset = formset_factory(
        request.POST or None,
        request.FILES or None,
        prefix=str(obj_field),
        queryset=obj_field.all(),
    )
    return formset


def create_forms(request, obj, form=None, only_seo=False):
    seo_data_form = SeoDataForm(
        request.POST or None,
        request.FILES or None,
        prefix="seo_form",
        instance=obj.seo_data,
    )
    if only_seo:
        return seo_data_form
    elif form:
        form1 = form(
            request.POST or None, request.FILES or None, prefix="form1", instance=obj
        )
        return form1, seo_data_form
    else:
        raise Exception('Func "create_forms" got wrong attributes')


def save_new_objects_to_many_to_many_field(field, new_objects_name, request):
    new_objects = request.FILES.getlist(f"{new_objects_name}")
    objects = []

    if field.model == GalleryImage:
        if new_objects:
            for new_obj in new_objects:
                obj = GalleryImage(image=new_obj)
                obj.save()
                objects.append(obj)

            field.add(*objects)

    elif field.model == Document:
        print(request.FILES)
        for file in request.FILES:
            pass
            # file = request.FILES.getlist(file)
            # name = request.POST.get(file.replace('file', 'name')) or 'Файл'
            # print(file, request.POST.get(file))
            # obj = Document(file=file, name=name)
            # obj.save()
            # objects.append(obj)
            # print(obj)

        field.add(*objects)

    else:
        raise Exception(
            "Function save_new_objects_to_many_to_many_field can't handle this ManyToManyField model type."
        )
