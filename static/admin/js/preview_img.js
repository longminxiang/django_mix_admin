(function ($) {
    $(function () {
        var items = [];
        var item_dicts = [];
        $('.readonly a, .file-upload a').each(function () {
            var url = $(this).attr('href');
            var ext = url.split('?')[0].split('.').reverse()[0].toLowerCase();
            if (['jpg', 'jpeg', 'png'].indexOf(ext) != -1) {
                $(this).attr('data-url', url);
                $(this).attr('href', '#');
                items.push(url);
                item_dicts.push({ src: url });
            }
        });

        $('.readonly a, .file-upload ').click(function () {
            var cnt_url = $(this).data().url;
            var ext = cnt_url.split('?')[0].split('.').reverse()[0].toLowerCase();
            if (['jpg', 'jpeg', 'png'].indexOf(ext) == -1) return;

            $.magnificPopup.open({
                items: item_dicts,
                gallery: {
                    enabled: true,
                },
                type: 'image',
            }, items.indexOf(cnt_url));
        });
    });
})(django.jQuery);

(function($) {
    window.preview_images = function(urls) {

        if (typeof urls == "string" && (urls.startsWith('.') || urls.startsWith('#'))) {
            var newUrls = [];
            $(urls).each(function() {
                newUrls.push($(this).attr('src'));
            })
            urls = newUrls;
        }

        var item_dicts = [];
        for (var url of urls) {
            item_dicts.push({src: url});
        }

        $.magnificPopup.open({
            items: item_dicts,
            gallery: {
                enabled: true,
            },
            type: 'image',
        });
    }
})(django.jQuery);