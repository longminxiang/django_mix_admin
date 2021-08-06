(function ($) {
  var MDatePicker = Vue.component('MDatePicker', {
    template: '<div style="display:block;float:left;"> \
        <el-date-picker v-model="value1" :id="id" :name="name" :format="format" :clearable="false" :type="type" :placeholder="placeholder"/> \
      </div>',
    props: ['id', 'name', 'placeholder', 'type', 'format'],
    data: function () {
      return {
        value1: ''
      };
    },
  });

  $(function () {
    $("input[data-mixtype=ele_date_picker]").each(function (idx, el) {
      $(el).after('<div id="' + el.id + '_edpicker"></div>');
      var datetype = $(el).data('datetype') || 'datetime';
      var format = datetype == 'date' ? 'yyyy/MM/dd' : 'yyyy/MM/dd HH:mm:ss';
      new MDatePicker({
        propsData: {
          id: el.id,
          name: el.name,
          type: datetype,
          format: format
        },
        data: {
          value1: el.value
        }
      }).$mount('#' + el.id + '_edpicker');
      $(el).remove();
    });
  });
})(django.jQuery)
