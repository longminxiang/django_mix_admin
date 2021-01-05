import traceback
from openpyxl import load_workbook
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect


class HeaderIndex:

    def __init__(self, headers):
        super().__init__()
        for k, v in self.__class__.__dict__.items():
            if k.startswith('__'):
                continue
            idx = -1
            if isinstance(v, str):
                idx = headers.index(v) if v in headers else -1
            elif isinstance(v, (tuple, list)):
                for vv in v:
                    idx = headers.index(vv) if vv in headers else -1
                    if idx != -1:
                        break
            setattr(self, k, idx)


class XlsxImporter:

    header_index_class = HeaderIndex

    def __init__(self, header_flag, request, **kwargs):
        super().__init__()
        self.request = request
        self.header_flag = header_flag
        self.error_messages = []

    def processing_value(self, value):
        pass

    def dispatch(self, request):
        f = request.FILES.get('file', None)
        if f is None:
            raise ValidationError('导入文件出错')
        if f.name.split('.')[-1] == 'xls':
            raise ValidationError('暂不支持xls格式，请另存为xlxs再导入')

        wb = load_workbook(f)
        ws = wb.worksheets[0]
        headers = []
        values = []
        # 预处理一下头和值
        for vals in ws.iter_rows(values_only=True):
            if not headers and self.header_flag in list(vals):
                headers = [v.strip().replace('\n', '') for v in vals if v is not None]
                print(headers)
                continue
            if not headers:
                continue

            if vals[0] is not None:
                values.append([str(v).strip() if isinstance(v, str) else v for v in vals])

        # 头
        h_idxs = self.header_index_class(headers)

        objs = []
        for value in values:
            message_prefix = '{}{}行：'.format(self.header_flag, value[h_idxs.header_flag_index])
            try:
                obj = self.processing_value(value)
                objs.append(obj)
            except Exception:
                print(message_prefix, '未确定错误:', traceback.format_exc(-3))
                self.error_messages.append(message_prefix + '存在错误')

            # 有错误及时抛出，20条一次
            if len(self.error_messages) >= 20:
                raise ValidationError(self.error_messages)

        # 在返回前再抛出错误
        if len(self.error_messages) > 0:
            raise ValidationError(self.error_messages)

        return HttpResponseRedirect(request.path)
