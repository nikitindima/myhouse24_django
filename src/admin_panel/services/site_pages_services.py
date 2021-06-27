from django.forms import modelformset_factory

from src.admin_panel.forms import ArticleForm, SiteHomeForm, SeoDataForm
from src.admin_panel.models import SiteHomePage, SeoData, Article


def get_or_create_site_home_page_obj():
    articles_count = 6
    obj = SiteHomePage.objects.first()
    if obj is None:
        seo_data = SeoData()
        seo_data.save()
        obj = SiteHomePage(seo_data=seo_data)
        obj.save()
    while obj.around_us.all().count() < articles_count:
        article = Article()
        article.save()
        obj.around_us.add(article)
    return obj


def create_formset_for_site_home_page(obj, request):
    formset_factory = modelformset_factory(
        Article, form=ArticleForm, fields=["title", "description", "image"], extra=0
    )
    formset = formset_factory(
        request.POST or None,
        request.FILES or None,
        prefix="formset",
        queryset=obj.around_us.all(),
    )
    return formset


def create_forms(obj, request):
    form1 = SiteHomeForm(
        request.POST or None, request.FILES or None, prefix="form1", instance=obj
    )
    seo_data_form = SeoDataForm(request.POST or None, request.FILES or None, prefix='seo_form', instance=obj.seo_data)
    return form1, seo_data_form
