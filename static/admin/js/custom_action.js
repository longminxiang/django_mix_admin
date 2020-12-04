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
        else {
            var fileInput = document.getElementById("changelist-form-file");
            if (fileInput) form.removeChild(fileInput);
            form.removeAttribute("enctype");
            form.submit();
        }
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
})(django.jQuery)