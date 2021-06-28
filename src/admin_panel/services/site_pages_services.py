from django.forms import modelformset_factory

from src.admin_panel.forms import ArticleForm, SiteHomeForm, SeoDataForm, GalleryImageForm, DocumentForm
from src.admin_panel.models import SiteHomePage, SeoData, Article, GalleryImage, Document


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


def create_formset(request, obj, formset_type):
    if formset_type is Article:
        formset_factory = modelformset_factory(
            Article, form=ArticleForm, fields=["title", "description", "image"], extra=1
        )
        formset = formset_factory(
            request.POST or None,
            request.FILES or None,
            prefix="formset_article",
            queryset=obj.around_us.all(),
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
            queryset=obj.docs.all(),
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


def create_forms(request, obj, form):
    form1 = form(
        request.POST or None, request.FILES or None, prefix="form1", instance=obj
    )
    seo_data_form = SeoDataForm(
        request.POST or None,
        request.FILES or None,
        prefix="seo_form",
        instance=obj.seo_data,
    )
    return form1, seo_data_form


def save_new_objects_to_many_to_many_field(field, new_objects_name, request):
    new_objects = request.FILES.getlist(f'{new_objects_name}')

    if new_objects:
        objects = []

        if field.model == GalleryImage:
            for new_obj in new_objects:
                obj = GalleryImage(image=new_obj)
                obj.save()
                objects.append(obj)

            field.add(*objects)

        elif field.model == Document:
            for new_obj in new_objects:
                obj = Document(file=new_obj, name=new_obj.name)
                obj.save()
                objects.append(obj)

            field.add(*objects)

        else:
            raise Exception(
                'Function save_new_objects_to_many_to_many_field can\'t handle this ManyToManyField model type.')
