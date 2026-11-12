$(function () {
    /* －－－－－－－－－－進階設定視窗－－－－－－－－－－ */
    //開啟進階設定視窗
    $('input#advance').click(function () {
        //取得位置
        var fieldOffset = $('img#img-menu').position();
        var H = $('div#side-menu-content-container').height() - 115;
        var offset = { top: fieldOffset.top + H, left: fieldOffset.left + 20 };
        $('div.advance').css('top', offset.top);
        $('div.advance').css('left', offset.left);
        $('div.advance').css('position', 'absolute');
        $('div.advance').show(500); //進階設定視窗

        //移動進階設定視窗的位置
        //$('div.advance').insertAfter('div#ccr-side-menu-clear-bar-layout');
        //$('div.advance').show(500); //進階設定視窗
        return false;
    });

    /* －－－－－－－－－－主選單切換視窗－－－－－－－－－－ */
    //首頁
    $('a.Home').click(function () {
        //取得網站URL
        var url = document.location.pathname;
        if (url.charAt(url.length - 1) != '/') {
            url = url + '/';
        }
        var id = $(this).attr('id');
        $('div.result-panel').remove();
        $('div.story').remove();
        $.ajax({    //使用非同步的方式載入該視窗
            url: url + 'Home/' + id,
            cache: false,
            success: function (html) {
                $('div#ResultMain').append(html); //將該視窗置於共用 DIV
            }
        });
        return false;
    });
    $('a.Home').hover(function () {
        $(this).css('text-decoration', 'underline');
        return false;
    }, function () {
        $(this).css('text-decoration', 'none');
        return false;
    });

    //簡介
    $('a.Introduction').click(function () {
        //取得網站URL
        var url = document.location.pathname;
        if (url.charAt(url.length - 1) != '/') {
            url = url + '/';
        }
        var id = $(this).attr('id');
        $('div.result-panel').remove();
        $('div.story').remove();
        $.ajax({    //使用非同步的方式載入該視窗
            url: url + 'Introduction/' + id,
            cache: false,
            success: function (html) {
                $('div#ResultMain').append(html); //將該視窗置於共用 DIV
            }
        });
        return false;
    });
    $('a.Introduction').hover(function () {
        $(this).css('text-decoration', 'underline');
        return false;
    }, function () {
        $(this).css('text-decoration', 'none');
        return false;
    });

    //收錄現況
    $('a.Statistics').click(function (event) {
        //取得網站URL
        var url = document.location.pathname;
        if (url.charAt(url.length - 1) != '/') {
            url = url + '/';
        }
        var id = $(this).attr('id');
        $('div.result-panel').remove();
        $('div.story').remove();
        $.ajax({    //使用非同步的方式載入該視窗
            url: url + 'Statistics/' + id,
            cache: false,
            success: function (html) {
                if ($('div.story').length == 0) { //判斷該個別視窗是否存在
                    $('div#ResultMain').append(html); //將該視窗置於共用 DIV
                    $('div#ResultMain').click();
                }                
            }
        });
        event.stopPropagation();
        return false;
    });
    $('a.Statistics').hover(function () {
        $(this).css('text-decoration', 'underline');
        return false;
    }, function () {
        $(this).css('text-decoration', 'none');
        return false;
    });

    //凡例
    $('a.Example').click(function () {
        //取得網站URL
        var url = document.location.pathname;
        if (url.charAt(url.length - 1) != '/') {
            url = url + '/';
        }
        var id = $(this).attr('id');
        $('div.result-panel').remove();
        $('div.story').remove();
        $.ajax({    //使用非同步的方式載入該視窗
            url: url + 'Example/' + id,
            cache: false,
            success: function (html) {
                $('div#ResultMain').append(html); //將該視窗置於共用 DIV
            }
        });
        return false;
    });
    $('a.Example').hover(function () {
        $(this).css('text-decoration', 'underline');
        return false;
    }, function () {
        $(this).css('text-decoration', 'none');
        return false;
    });

    //使用說明
    $('a.Help').click(function () {
        //取得網站URL
        var url = document.location.pathname;
        if (url.charAt(url.length - 1) != '/') {
            url = url + '/';
        }
        var id = $(this).attr('id');
        $('div.result-panel').remove();
        $('div.story').remove();
        $.ajax({    //使用非同步的方式載入該視窗
            url: url + 'Help/' + id,
            cache: false,
            success: function (html) {
                $('div#ResultMain').append(html); //將該視窗置於共用 DIV
            }
        });
        return false;
    });
    $('a.Help').hover(function () {
        $(this).css('text-decoration', 'underline');
        return false;
    }, function () {
        $(this).css('text-decoration', 'none');
        return false;
    });

    //參考書目（下拉式表單）
    $('a.Bibliography').click(function () {
        //取得網站URL
        var url = document.location.pathname;
        if (url.charAt(url.length - 1) != '/') {
            url = url + '/';
        }
        var id = $(this).attr('id');
        $('div.result-panel').remove();
        $('div.story').remove();
        $.ajax({    //使用非同步的方式載入該視窗
            url: url + 'Bibliography/' + id,
            cache: false,
            success: function (html) {
                $('div#ResultMain').append(html); //將該視窗置於共用 DIV
            }
        });
        return false;
    });
    $('a.Bibliography').hover(function () {
        $(this).css('text-decoration', 'underline');
        return false;
    }, function () {
        $(this).css('text-decoration', 'none');
        return false;
    });

    //聯絡信箱
    $('a#Email').hover(function () {
        $(this).css('text-decoration', 'underline');
        return false;
    }, function () {
        $(this).css('text-decoration', 'none');
        return false;
    });

    $('div#ResultMain').bind('click', function () {
        $('a.XianDai').click(function (event) {
            var id = $(this).attr('id');
            $('a#' + id + '.Statistics').click();
            event.stopPropagation();
            return false;
        });

    });
});