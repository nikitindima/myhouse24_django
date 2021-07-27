import os

from django.contrib.staticfiles import finders
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

from config import settings


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    print(1)
    result = finders.find(uri)
    print(result, 'result')

    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path = result[0]
        print(path)
    else:
        sUrl = settings.STATIC_URL  # Typically /static/
        mUrl = settings.MEDIA_URL  # Typically /media/
        s_root = settings.STATIC_ROOT  # Typically /home/userX/project_static/
        m_root = settings.MEDIA_ROOT  # Typically /home/userX/project_static/media/

        if uri.startswith(mUrl):
            path = os.path.join(m_root, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(s_root, uri.replace(sUrl, ""))
        else:
            return uri
    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path


class PdfFactory:
    def __init__(self, template_path, context, filename='file'):
        self.template_path = template_path
        self.context = context
        self.filename = filename
        self.response = self.prepare_response()
        self.template = get_template(self.template_path)
        self.html = self.template.render(self.context)
        self.create_pdf_response()

    def prepare_response(self):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{self.filename}.pdf"'
        return response

    def create_pdf_response(self):
        pisa_status = pisa.CreatePDF(
            self.html, dest=self.response, link_callback=link_callback, encoding="UTF-8"
        )

        if pisa_status.err:
            return HttpResponse('Ошибка! --> <pre>' + self.html + '</pre>')

    def get_response(self):
        return self.response
