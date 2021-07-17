function updateFormIndex(element, prefix, index) {
    let id_regex = new RegExp('(' + prefix + '-\\d+)');
	let replacement = prefix + '-' + index;
	let name = $(this).attr('name').replace(id_regex,replacement);
	let id = 'id_' + name;
    $(this).attr({'name': name, 'id': id}).val('');
}

function delForm(btn, prefix, form, counter) {
    $(btn).parents(form).remove();
    let forms = $(form);
    total = $('#id_' + prefix + '-TOTAL_FORMS').val() - 1
    $('#id_' + prefix + '-TOTAL_FORMS').val(total);

    for (var i=1, formCount=forms.length; i<formCount; i++) {
        element = $(forms.get(i));
        element.find(':input').each(function() {
            updateFormIndex(element, prefix, i-1)
        });
        if (counter) element.find(counter).text(i);
    }
    return false;
}

function addForm(prefix, form, counter) {
    let selector_first = form + ":first";
    let selector_last = form + ":last";
    let newElement = $(selector_first).clone(true);
    let total = $('#id_' + prefix + '-TOTAL_FORMS').val();
    let i = 0;

    newElement.find('input, textarea').each(function() {
        let name = prefix + '-' + total + '-' + $(this).attr('name');
        let id = 'id_' + name;
        $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
    });
    newElement.css('display', '')

    total++;
    $('#id_' + prefix + '-TOTAL_FORMS').val(total);
    if (counter) newElement.find(counter).each(function() { $(this).text(total); });
    $(selector_last).after(newElement);

    let attr_id = newElement.find('textarea').attr('id');

    tinymce.init({selector:'#'+attr_id});
}

function addHiddenForm(prefix, form_class, image_class, default_image_url){
    let selector = form_class + ":first";
    let element = $(selector).clone(true);

    element.find(':input').each(function() {
        let name = $(this).attr('name').replace(prefix + '-0-','');
        let id = 'id_' + name;
        $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
    });
    if (default_image_url) element.find(image_class).each(function() {
        $(this).css('background', 'url(' + default_image_url + ') no-repeat');
    });
    element.find('textarea').addClass('hidden_textarea');
    element.css('display', 'none');
    $(selector).before(element);
}
function addChoiseForm(prefix, form, counter) {
    let selector_first = form + ":first";
    let selector_last = form + ":last";
    let newElement = $(selector_first).clone(true);
    let total = $('#id_' + prefix + '-TOTAL_FORMS').val();
    let i = 0;
    var result = []

    newElement.find('input, select').each(function () {
        let name = prefix + '-' + total + '-' + $(this).attr('name');
        let id = 'id_' + name;
        result.push(id)
        $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
    });
    newElement.css('display', '')

    total++;
    $('#id_' + prefix + '-TOTAL_FORMS').val(total);
    if (counter) newElement.find(counter).each(function () {
        $(this).text(total);
    });
    $(selector_last).after(newElement);

    let attr_id = newElement.find('select').attr('id');

    return result
}

function requestWithoutReload(url, data){
     event.preventDefault();
      $.ajax({
         type: "POST",
         url: url,
         data: data,
         success: function() {
          }
     });
}