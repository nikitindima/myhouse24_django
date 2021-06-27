def validate_multiple_forms_and_append(iterable_obj, append_to):
    for form in iterable_obj:
        if form.is_valid():
            append_to.append(True)
        else:
            append_to.append(False)


def validate_forms(*args, formset=None):
    validation_list = []
    if args:
        validate_multiple_forms_and_append(args, append_to=validation_list)

    if formset:
        validation_list.append(formset.is_valid())
        validate_multiple_forms_and_append(formset, append_to=validation_list)

    if all(validation_list):
        return True
    else:
        return False


def save_forms(*args):
    for form in args:
        form.save(commit=True)
