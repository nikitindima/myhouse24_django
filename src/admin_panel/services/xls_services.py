import io

from xlsxwriter import Workbook


def make_in_memory_worksheet(columns):
    output = io.BytesIO()

    workbook = Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    for column in columns:
        worksheet.write(0, columns.index(column), column)

    worksheet.set_default_row(70)

    cell_format = workbook.add_format()
    cell_format.set_text_wrap()

    return cell_format, output, workbook, worksheet
