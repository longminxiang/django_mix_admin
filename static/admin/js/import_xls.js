if (typeof $ == 'undefined') $ = django.jQuery;

function import_file(action, idf, accept) {
    var input = document.createElement("input");
    input.type = "file";
    if (typeof accept != "undefined") input.accept = accept;
    input.click();
    input.onchange = function(){
        var file = input.files[0];
        var form = new FormData();
        form.append("file", file);
        form.append("_import", idf);
        form.append("csrfmiddlewaretoken", document.getElementById("changelist-form").csrfmiddlewaretoken.value);
        var xhr = new XMLHttpRequest();
        xhr.open("POST", action);
        xhr.send(form);
        xhr.onreadystatechange = function(){
            if (xhr.readyState==4 && xhr.status==200){
                var res = JSON.parse(xhr.responseText);
                var messagelist = $(".messagelist").first();
                var cls = res.code == 1 ? "success" : "error";
                if (messagelist.length) {
                    messagelist.html('<li class="' + cls + '">' + res.message + '</li>')
                }
                else {
                    var messagelist = '<ul class="messagelist"><li class="' + cls +'">' + res.message + '</li></ul>';
                    $(".breadcrumbs").first().after(messagelist);
                }
            }
        }
    }
}
