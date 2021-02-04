(function ($) {
    $(function () {

      $("input[data-mixtype=laydate]").each(function (idx, el) {
        laydate.render({elem: el, format: 'yyyy/MM/dd', theme: '#417690'});
      });

      $("input[data-mixtype=laydatetime]").each(function (idx, el) {
        laydate.render({elem: el, type: 'datetime', format: 'yyyy/MM/dd HH:mm', theme: '#417690'});
      });

    });
  })(django.jQuery)
  