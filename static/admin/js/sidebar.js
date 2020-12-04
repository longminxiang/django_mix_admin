(function ($) {
    $(function () {
        $(".x-sidebar-item a").click(function () {
            var icon = $(this).find(".x-sidebar-item-icon");
            if (icon.hasClass("x-sidebar-item-icon-normal")) {
                icon.removeClass("x-sidebar-item-icon-normal");
                icon.addClass("x-sidebar-item-icon-active");
            }
            else {
                icon.removeClass("x-sidebar-item-icon-active");
                icon.addClass("x-sidebar-item-icon-normal");
            }
            $(this).parent().find(".x-sidebar-menu-sub").toggle();
        });
    });
})(django.jQuery)