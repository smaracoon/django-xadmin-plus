jQuery(function($){
    //full screen btn
    $('.layout-btns .layout-full').click(function(e){
        var icon = $(this).find('i')
        if($(this).hasClass('active')){
            // reset
            $('#left-side, ul.breadcrumb').show('fast');
            $('#content-block').removeClass('col-md-12 col-sm-12 full-content').addClass('col-sm-11 col-md-11');
            icon.removeClass('fa-compress-arrows-alt').addClass('fa-expand-arrows-alt');
            $(window).trigger('resize');
        } else {
            // full screen
            $('#left-side, ul.breadcrumb').hide('fast', function(){
                $('#content-block').removeClass('col-sm-11 col-md-11').addClass('col-md-12 col-sm-12 full-content');
                icon.removeClass('fa-expand-arrows-alt').addClass('fa-compress-arrows-alt');
                $(window).trigger('resize');
            });
        }
    });

    $('.layout-btns .layout-normal').click(function(e){
        $('.results table').removeClass('table-condensed');
    });

    $('.layout-btns .layout-condensed').click(function(e){
        $('.results table').addClass('table-condensed');
    });

});