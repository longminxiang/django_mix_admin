window.onload = function () {
    var items = [];
    var item_dicts = [];
    $('.readonly a').each(function () {
        var url = $(this).attr('href');
        $(this).attr('data-url', url);
        $(this).attr('href', '#');
        items.push(url);
        item_dicts.push({ src: url });
    });

    $('.readonly a').click(function () {
        var cnt_url = $(this).data().url;

        $.magnificPopup.open({
            items: item_dicts,
            gallery: {
                enabled: true,
            },
            type: 'image',
        }, items.indexOf(cnt_url));
    });
}