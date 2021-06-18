import io
from openpyxl import Workbook
from django.utils import timezone
from django.http import HttpResponse


class XlsxExporter:

    def _get_objs(self):
        pass

    def _process(self, obj):
        pass

    def _pre_dispatch(self, wb, ws):
        pass

    def dispatch(self):
        wb = Workbook()
        ws = wb.active

        self._pre_dispatch(wb, ws)
        objs = self._get_objs()
        for obj in objs:
            vals = self._process(obj)
            ws.append(vals)

        f = io.BytesIO()
        wb.save(f)
        f.seek(0)
        data = f.read()
        f.close()
        response = HttpResponse(
            data,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = "attachment;filename={}.xlsx".format(
            timezone.make_naive(timezone.now()).strftime("%Y%m%d%H%M%S"))
        return response
