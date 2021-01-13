(function ($) {

  function createVueElement(el) {
    var options;
     try {
      options = JSON.parse(el.dataset.options);
    } catch (error) {
      options = {}
    }
    if (typeof el.dataset.disabled != "undefined") options.disabled = el.dataset.disabled;

    var value;
    try {
      value = JSON.parse(el.value);
    } catch (error) {
      value = {}
    }
    var vueElementId = el.id + '_uploader';
    var vueElementRef = el.id + '_fileagent';

    var vueHtml = '<div id="' + vueElementId + '" style="display:block; float:left; max-width: 800px;"> \
      <vue-file-agent \
        ref="' + vueElementRef + '" \
        :multiple="true" \
        :deletable="' + (options.disabled ? 'false' : 'true') + '" \
        :linkable="true" \
        :sortable="' + (options.disabled ? 'false' : '\'handle\'') + '" \
        :meta="false" \
        accept="' + (options.accept || '*') + '" \
        max-size="' + (options.maxsize || '10M') + '" \
        :max-files="' + (options.disabled ? 1 : (options.maxfiles || 1)) + '" \
        help-text="' + (options.helptext || '') + '" \
        error-text="'+ (options.errortext || {}) + '" \
        @select="filesSelected($event)" \
        @beforedelete="onBeforeDelete($event)" \
        @upload="onUpload($event)" \
        v-model="fileRecords" \
      /> \
    </div>';

    $(el).hide();
    $(el).after(vueHtml);

    el.vm = new Vue({
      el: '#' + vueElementId,
      data: function () {
        return {
          fileRecords: (value && value.files) || [],
          uploading: false,
          uploadingError: false,
        };
      },
      mounted: function() {
        fixPreview(el);
      },
      methods: {
        filesSelected: function (fileRecordsNewlySelected) {
          var fileRecords = fileRecordsNewlySelected.filter(function (record) {
            return !record.error ? record : undefined;
          });

          if (options.presignedupload) {
            for (var i = 0; i < fileRecords.length; i++) {
              var record = fileRecords[i];

              $.get(options.presignedupload.url + '?name=' + record.file.name + (options.presignedupload.extra || ''), function (res) {
                if (res.code == 1) {
                  var record = fileRecords.filter(function (r) { return r.file.name == res.data.name ? r : undefined })[0];
                  record.uploading = true;
                  this.$refs[vueElementRef].upload(res.data.url, {}, [record], function () {
                    return record.file;
                  }, function (request) {
                    request.open('PUT', res.data.url, true);
                    request.setRequestHeader("Content-Type", record.type);
                  });
                }
              }.bind(this));
            }
          }
          else if (options.upload) {
            this.$refs[vueElementRef].upload(options.upload.url, options.upload.header, validFileRecords);
          }
        },
        onBeforeDelete: function (fileRecord) {
          if (confirm('是否确认删除?')) {
            this.$refs[vueElementRef].deleteFileRecord(fileRecord);
          }
        },
        onUpload: function (responses) {
          for (var response of responses) {
            if (response.error) {
              this.uploadingError = true;
              continue;
            }
            var record = response.fileRecord;
            record.uploading = false;
            record.final_url = response.request.responseURL.split('?')[0];
          }
          fixPreview(el);
        }
      },
    });
  }

  function checkUploading(el) {
    if (el.vm.uploadingError) {
      confirm('上传错误，请删除或重新上传后再保存');
      return false;
    }
    else if (el.vm.uploading) {
      confirm('文件上传中');
      return false;
    }
    else {
      var files = [];
      for (var record of el.vm.fileRecords) {
        if (record.error) {
          confirm('上传错误，请删除或重新上传后再保存');
          return false;
        }
        var url = record.final_url || (typeof record.url == "function" ? record.url() : record.url);
        var name = typeof record.name == "function" ? record.name() : record.name;
        files.push({ url: url, name: name, size: record.size, type: record.type });
      }
      $(el).val(JSON.stringify({ files: files }));
    }
    return true;
  }

  function fixPreview(el) {
    setTimeout(function() {
      var acts = $(".file-av-action");
      acts.after('<div class="file-av-action">\
        <span class="file-av-play"> \
          <svg viewBox="0 0 48 48"> \
            <path d="M24 4C12.95 4 4 12.95 4 24s8.95 20 20 20 20-8.95 20-20S35.05 4 24 4zm-4 29V15l12 9-12 9z"></path> \
          </svg> \
        </span></div>');
      acts.remove();

      var els = $(".file-preview-wrapper").find(".thumbnail, .file-icon, .file-av-action");
      els.off('click');
      els.click(function(e) {
        var index = $(".file-preview-wrapper").index($(this).parentsUntil('.file-preview-wrapper').parent()[0]);
        e.preventDefault();
        var urls = [];
        for (var record of el.vm.fileRecords) {
          var url = typeof record.url == "function" ? record.url() : record.url;
          if (!url) url = record.final_url;
          if (url) urls.push(url);
        }
        preview_files(urls, index || 0);
      });
    }, 500);
  }

  $(function () {

    var els = $("input[data-ftype=fileagent]");
    if (els.length == 0) return;

    els.each(function(idx, el) {
      createVueElement(el);
    });

    if (window.VueSlicksort) {
      Vue.component('vfa-sortable-list', window.VueSlicksort.SlickList);
      Vue.component('vfa-sortable-item', window.VueSlicksort.SlickItem);
    }

    $("input[type=submit]").click(function (e) {
      $("input[data-ftype=fileagent]").each(function(idx, el) {
        var success = checkUploading(el);
        if (!success) {
          e.preventDefault();
        }
      });
    })
  });
})(django.jQuery)
