(function ($) {
    window.preview_video = function (url, close_callback) {
        $('#mix-video-container').remove();
        $('body').append('<div id="mix-video-container" style="position:absolute;left:0;bottom:0;right:0;top:0;overflow:hidden;z-index:999999"> \
            <div style="display:flex;justify-content:center;align-items:center;height:100%;"> \
                <div style="width:80%;"> \
                    <a href="#" id="mix-video-close-btn" style="color: #fff;">关闭</a> \
                    <video id="mix-video-player" class="video-js vjs-big-play-centered vjs-fluid" controls autoplay data-setup="{}"> \
                        <source src="' + url + '"></source> \
                    </video> \
                </div> \
            </div></div>');
        window.mix_video_player = videojs('#mix-video-player');
        $('#mix-video-close-btn').click(function () {
            remove_preview_video();
            if (typeof close_callback == "function") close_callback()
        });
        return window.mix_video_player;
    }

    window.remove_preview_video = function () {
        $('#mix-video-container').remove();
        window.mix_video_player && window.mix_video_player.dispose();
    }

    window.preview_images = function (urls, index) {

        if (typeof urls == "string" && (urls.startsWith('.') || urls.startsWith('#'))) {
            var newUrls = [];
            $(urls).each(function () {
                newUrls.push($(this).attr('src'));
            })
            urls = newUrls;
        }

        $("#images-for-viewer").remove()
        $("body").append('<div id="images-for-viewer" style="display:none;"></div>')

        for (var url of urls) {
            var ext = url.split('?')[0].split('.').reverse()[0].toLowerCase();
            var dataMediaUrl = '';
            if (ext == 'mp4') {
                dataMediaUrl = 'data-mediaUrl="' + url + '" ';
                url = '/static/admin/img/player1.jpg';
            }
            else if (['jpg', 'png', 'jpeg', 'gif'].indexOf(ext) == -1) {
                dataMediaUrl = 'data-fileUrl="' + url + '" ';
                url = '/static/admin/img/file.jpg';
            }
            $("#images-for-viewer").append('<img ' + dataMediaUrl + ' data-original="' + url + '" />');
        }

        index = index || 0;
        index = index >= urls.length ? 0 : index;
        var viewer;
        var images_for_viewer = document.getElementById("images-for-viewer");
        viewer = new Viewer(images_for_viewer, {
            url: 'data-original', scalable: false, initialViewIndex: index, viewed: function () {
                var image = viewer.images[viewer.index];
                var mediaUrl = $(image).data().mediaurl;
                if (mediaUrl) {
                    $(".viewer-canvas img").click(function (e) {
                        $('.viewer-canvas, .viewer-footer, .viewer-close').hide();
                        preview_video(mediaUrl, function() {
                            $('.viewer-canvas, .viewer-footer, .viewer-close').show();
                        });
                    })
                }
            }
        });
        viewer.show();
    }

})(django.jQuery);

(function ($) {
    $(function () {

        $('.readonly a, .file-upload a').click(function (e) {
            e.preventDefault();

            var cnt_url = $(this).attr('href');
            var ext = cnt_url.split('?')[0].split('.').reverse()[0].toLowerCase();

            var image_urls_for_viewer = [];
            $('.readonly a, .file-upload a').each(function () {
                var url = $(this).attr('href');
                var ext = url.split('?')[0].split('.').reverse()[0].toLowerCase();
                image_urls_for_viewer.push(url);
            });

            preview_images(image_urls_for_viewer, image_urls_for_viewer.indexOf(cnt_url));

        });
    });
})(django.jQuery);
