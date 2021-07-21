import random

from django import forms
from django.contrib import messages
from django.forms import modelformset_factory
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _

from src.admin_panel.models import Section, Measure, Service


def validate_multiple_forms_and_append(iterable_obj, append_to):
    for form in iterable_obj:
        if form.is_valid():
            append_to.append(True)
        else:
            append_to.append(False)


def validate_forms(*args, formset=None, document_formset=None):
    validation_list = []
    if args:
        validate_multiple_forms_and_append(args, append_to=validation_list)

    if formset:
        validation_list.append(formset.is_valid())
        validate_multiple_forms_and_append(formset, append_to=validation_list)

    if document_formset:
        validation_list.append(document_formset.is_valid())
        validate_document_formset_forms_and_append(
            document_formset, append_to=validation_list
        )

    if all(validation_list):
        return True
    else:
        return False


def save_forms(*args):
    for form in args:
        form.save(commit=True)


def validate_document_formset_forms_and_append(iterable_obj, append_to):
    for form in iterable_obj:
        if form.is_valid():
            if form.cleaned_data != {}:
                append_to.append(True)
            else:
                form.add_error("file", "Обязательное поле")
                form.add_error("name", "Обязательное поле")
                append_to.append(False)
        else:
            append_to.append(False)


def check_filesize(uploaded_file, max_upload_size):
    if uploaded_file.size > max_upload_size:
        # check if the file has a valid size
        raise forms.ValidationError(
            _("Пожалуйста, загрузите файл с размером меньше %s. Текущий размер %s")
            % (filesizeformat(max_upload_size), filesizeformat(uploaded_file.size))
        )


def validate_image(form, name, max_size=None):
    uploaded_file = form.cleaned_data.get(name)
    if uploaded_file is not None:

        if max_size:
            check_filesize(uploaded_file, max_size)
        try:
            # check if the file is a valid image
            img = forms.ImageField()
            img.to_python(uploaded_file)
        except forms.ValidationError:
            raise forms.ValidationError("Вы можете загружать только изображения")


def create_formset(form, request, post=False, qs=None, can_delete=False, prefix='formset_sections', files=False, extra=0):
    formset_factory = modelformset_factory(
        model=form.Meta.model, form=form, can_delete=can_delete, extra=extra
    )
    formset = formset_factory(
        request.POST or None,
        prefix=prefix,
    )

    if post:
        formset.data = request.POST or None
    if files:
        formset.files = request.FILES or None
    if qs is None:
        formset.queryset = form.Meta.model.objects.none()
    else:
        formset.queryset = qs

    return formset


def save_extra_forms(formset, model, **kwargs):
    for form in formset.extra_forms:
        if form.cleaned_data.get("name"):
            name = form.cleaned_data.get("name")

            if model is Section:
                new_object = Section(name=name, house=kwargs["house"], floors=form.cleaned_data.get("floors"))
            elif model is Measure:
                new_object = Measure(name=name)
            elif model is Service:
                continue
                # new_object = Measure(name=name)
            else:
                raise Exception(
                    'You passed wrong model type to "save_extra_forms" function'
                )

            new_object.full_clean()
            new_object.save()


def send_form_errors_to_messages_framework(form, request, formset=False):
    if formset is True:
        form_errors = form.errors[0]
    else:
        form_errors = form.errors

    if form.errors:
        [
            messages.error(request, f"{field}, {error.as_text()}")
            for field, error in form_errors.items()
        ]


def generate_random_number_for_model_field(model=None, field=None, length=10):
    while True:
        range_start = 10**(length-1)
        range_end = (10**length)-1

        number = random.randint(range_start, range_end)

        if model is not None and field is not None:
            qs_filter = field + '__' + 'contains'
            qs = model.objects.filter(**{qs_filter: number})
            if qs.exists():
                continue
            else:
                break
        else:
            break

    return number
