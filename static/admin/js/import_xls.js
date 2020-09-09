function import_file(action, idf, accept) {
    var input = document.createElement("input");
    input.name = 'file';
    input.type = "file";
    if (typeof accept != "undefined") input.accept = accept;

    $(input).change(function () {
        var form = document.createElement("form");
        form.enctype = 'multipart/form-data';
        form.action = action;
        form.method = "post";
        form.style.display = "none";

        form.appendChild(input);

        var opt1 = document.createElement("input");
        opt1.name = "_import";
        opt1.value = idf;
        form.appendChild(opt1);

        var opt2 = document.createElement("input");
        opt2.name = "csrfmiddlewaretoken";
        opt2.value = document.getElementById("changelist-form").csrfmiddlewaretoken.value;
        form.appendChild(opt2);

        document.body.appendChild(form);
        form.submit();
    });

    input.click();
}
