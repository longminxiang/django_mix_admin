(function ($) {
    function _getOrCreateInput(form, id, name, progress) {
        var input = document.getElementById(id);
        if (!input) {
            input = document.createElement("input");
            input.setAttribute("id", id);
            input.setAttribute("name", name);
            input.style.visibility = "hidden";
            if (typeof progress == "function") progress(input);
            form.appendChild(input);
        }
        return input
    }

    function _perform_action(action, options) {
        var form = document.getElementById("changelist-form");

        var actionInput = _getOrCreateInput(form, "changelist-form-action", "action");
        actionInput.setAttribute("value", action);

        var indexInput = _getOrCreateInput(form, "changelist-form-index", "index");
        indexInput.setAttribute("value", 1);

        if (options.without_queryset) {
            var selectedActionInput = _getOrCreateInput(form, "changelist-form-selected-action", "_selected_action");
            selectedActionInput.setAttribute("value", 1);
        }
        else {
            var selectedActionInput = document.getElementById("changelist-form-selected-action");
            if (selectedActionInput) form.removeChild(selectedActionInput);
        }

        // 导入文件
        if (options.import_file) {
            var fileInput = _getOrCreateInput(form, "changelist-form-file", "file", function (input) {
                input.type = "file";
                form.enctype = "multipart/form-data";
                $(input).change(function () {
                    form.submit();
                });
            });
            if (options.accept) fileInput.accept = options.accept;
            fileInput.click();
        }
        else if (options.ajax) {
            var ajax = window.mix_custom_action_ajaxs && window.mix_custom_action_ajaxs[options.name];
            if (typeof ajax == "function") {
                var formData = new FormData(form);
                var across = formData.get('select_across');
                var selecteds = formData.getAll('_selected_action');
                ajax({ across: across, selecteds: selecteds });
            }
        }
        else {
            var fileInput = document.getElementById("changelist-form-file");
            if (fileInput) form.removeChild(fileInput);
            form.removeAttribute("enctype");
            form.submit();
        }
    };

    window.mix_custom_action_add_ajax = function (name, func) {
        if (typeof window.mix_custom_action_ajaxs == "undefined") {
            window.mix_custom_action_ajaxs = [];
        }
        window.mix_custom_action_ajaxs[name] = func;
    };

    window.mix_custom_action = function (action, options) {
        options = options || {};
        if (options.confirm) {
            swal.fire({
                title: "提示", text: options.confirm_message || "确认执行",
                confirmButtonText: "确定",
                cancelButtonText: "取消",
                showCancelButton: true
            })
                .then(function (t) {
                    if (t.isConfirmed) {
                        _perform_action(action, options);
                    }
                });
        }
        else {
            _perform_action(action, options);
        }
        return false;
    }

    // req: {bucketName: bucketName, prefix: prefix, objects: objects}
    window.downloadMinioZip = function (url, req) {
        var anchor = document.createElement("a")
        document.body.appendChild(anchor)

        var xhr = new XMLHttpRequest()
        xhr.open("POST", url, true)
        xhr.responseType = "blob"

        mixLoading.show(20000);
        xhr.onload = function (e) {
            if (this.status == 200) {
                var blob = new Blob([this.response], {
                    type: "octet/stream",
                })
                var blobUrl = window.URL.createObjectURL(blob)
                var separator = req.prefix.length > 1 ? "-" : ""

                anchor.href = blobUrl
                anchor.download = req.bucketName + separator + req.prefix.slice(0, -1) + ".zip"

                anchor.click()
                window.URL.revokeObjectURL(blobUrl)
                anchor.remove()
                mixLoading.hide();
            }
        }
        xhr.send(JSON.stringify(req))
    }

    window.mixLoading = {
        timeoutHandle: undefined,
        show: function (timeout) {
            var loadingHtml = '<div class="sk-circle"> \
                <div class="sk-circle1 sk-child"></div> \
                <div class="sk-circle2 sk-child"></div> \
                <div class="sk-circle3 sk-child"></div> \
                <div class="sk-circle4 sk-child"></div> \
                <div class="sk-circle5 sk-child"></div> \
                <div class="sk-circle6 sk-child"></div> \
                <div class="sk-circle7 sk-child"></div> \
                <div class="sk-circle8 sk-child"></div> \
                <div class="sk-circle9 sk-child"></div> \
                <div class="sk-circle10 sk-child"></div> \
                <div class="sk-circle11 sk-child"></div> \
                <div class="sk-circle12 sk-child"></div> \
            </div>';
            swal.fire({
                html: loadingHtml, showConfirmButton: false, background: 'transparent', width: 'unset',
                allowOutsideClick: false,
            });
            mixLoading.timeoutHandle = setTimeout(function () {
                mixLoading.hide();
            }, timeout || 10000);
        },
        hide: function () {
            swal.close();
            mixLoading.timeoutHandle && clearTimeout(mixLoading.timeoutHandle);
        }
    }

})(django.jQuery)