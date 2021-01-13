(function ($) {
    window.preview_files = function (urls, index) {
        if (!urls || !urls.length) return;
        if (typeof urls == "string" && (urls.startsWith('.') || urls.startsWith('#'))) {
            var newUrls = [];
            $(urls).each(function () {
                newUrls.push($(this).attr('src'));
            })
            urls = newUrls;
        }

        index = index && index < 0 ? 0: index;
        var items = [];
        for (var url of urls) {
            var ext = url.split('?')[0].split('.').reverse()[0].toLowerCase();
            var shtml;
            if (['mp3', 'mp4', 'wmv', 'mpg'].indexOf(ext) != -1) {
                shtml = '<div style="width:800px;"> \
                    <script>window.mix_video_player && window.mix_video_player.dispose();</script> \
                    <video id="mix-video-player" class="video-js vjs-big-play-centered vjs-fluid" controls data-setup="{}"> \
                        <source src="' + url + '"></source> \
                    </video> \
                    <script>window.mix_video_player = videojs("#mix-video-player");</script></div>'
            }
            else if (['doc', 'docx', 'pdf', 'ppt', 'pptx', 'txt', 'xls', 'xlsx'].indexOf(ext) != -1) {
                var surl = "https://doc.gxpx365.com/view/url/?url=" + encodeURIComponent(url);
                shtml = '<iframe style="background-color:#eee;" id="mix-preview-iframe" frameborder=0 src="' + surl + '"></div>';
            }
            else {
                shtml = '<img id="mix-preview-img" src="' + url + '"/>';
            }
            items.push({src: '<div style="display:flex;justify-content:center;">' + shtml + '</div>', type: 'inline'});
        }
        $.magnificPopup.open({
            closeOnBgClick: false,
            closeBtnInside: false,
            autoFocusLast: false,
            items: items,
            gallery: {
                enabled: true
            },
            type: 'image',
            callbacks: {
                change: function() {
                    var miframe = $(this.content).find("#mix-preview-iframe");
                    miframe.width($(window).width() * 0.8);
                    miframe.height($(window).height() * 0.9);

                    var mimg = $(this.content).find("#mix-preview-img");
                    var src = mimg.length >= 1 && mimg[0].src;
                    if (src) {
                        var cb = function(img) {
                            if (img.height > $(window).height()) {
                                mimg.height($(window).height() * 0.9);
                            }
                        }
                        var img = new Image();
                        img.src = src;
                        if (img.complete) {
                            cb(img);
                        }
                        else {
                            img.onload = function() {
                                cb(img);
                            }
                        }
                    }
                }
            }
        }, index);
    }

})(django.jQuery);

(function ($) {
    $(function () {

        $('.readonly a, .file-upload a').not('.download').click(function (e) {
            e.preventDefault();

            var cnt_url = $(this).attr('href');

            var urls = [];
            $('.readonly a, .file-upload a').not('.download').each(function () {
                var url = $(this).attr('href');
                urls.push(url);
            });

            preview_files(urls, urls.indexOf(cnt_url));

        });
    });
})(django.jQuery);
