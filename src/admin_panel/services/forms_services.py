from django import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _


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
