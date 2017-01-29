/*  之後重構把功能聚集在這邊  */
var dataAjaxLoad = function(data, href){
    var $container = $('div#main-wrapper'),
        $script_container = $('script#main'),
        $token_container = $('script#token'),
        $data_div = $('<div></div>').html(data),
        $content = $data_div.find('div#main-wrapper'),
        $script = $data_div.find('script#main'),
        $token = $data_div.find('script#token'),
        $title = $data_div.find('title'),
        $log_btn = $data_div.find('div#nav li#log-btn'),
        $ul_dropdown = $data_div.find('ul.dropdown-menu');

    $container.html($content.html());
    $script_container.html($script.html());
    $token_container.html($token.html());
    document.title = $title.text();
//  update log-btn and menu to handle login/logout
    $('div#nav li#log-btn').html($log_btn.html());
    $('ul.dropdown-menu').html($ul_dropdown.html());

    eval($token.html());
    eval($script.html());
//  exclude log_btn to behave properly while login/logout
    history.pushState(
        {'html':$container.html(), 'script': $script.html(), 'title': $title.text()},
        $title.text(),
        href
    )
};

var ajaxSongPlay = function(url){
    $.ajax({
        type: "GET",
        'url': url,
        dataType: "html",
        success : function(data){
            $(data).prependTo(audioplayer.playQueue)
                   .find('i.queue-play-btn').trigger('click');
        },
        error: function(){ alert('錯誤') }
    });
}

var ajaxAlbumPlaylistPlay = function(url){
    $.ajax({
        type: "GET",
        url: url,
        dataType: "html",
        success : function(data){
            $(data).prependTo(audioplayer.playQueue.empty());
            audioplayer.forwardButton.trigger('click');
        },
        error: function(){ alert('錯誤') }
    });
}

var ajaxSongUtilsSet = function(song_id, selector, csrf_token){
// song-like-btn
    $('i.song-like-btn').on('click', function(){
        var $this = $(this),
            like_num = parseInt($this.text()),
            action = $this.hasClass('fa-heart-o') ? 'like': 'unlike',
            id = (song_id != null) ? song_id : $this.closest(selector).data('id');

        $.ajax({
            type: "POST",
            headers: {'X-CSRFToken': csrf_token},
            url: urlMusicSongLike,
            data: {
                'song_id': id,
                'action': action,
            },
            success : function(data, string, xhr){
                var content_type = xhr.getResponseHeader('Content-Type');
                if (xhr.status == 278) {
                    var url = xhr.getResponseHeader('Location'),
                        pos = url.indexOf('?next='),
                        redirect_url = url.slice(0, pos+6) + window.location.pathname;
                    $.get(redirect_url, function(data){
                        dataAjaxLoad(data, redirect_url);
                    })
                }
                else {
                    if (action == 'like') {
                        $this.removeClass('fa-heart-o').addClass('fa-heart red')
                                                       .text(' ' + (like_num+1));
                    }
                    else {
                        $this.removeClass('fa-heart red').addClass('fa-heart-o')
                                                       .text(' ' + (like_num-1));
                    }
                }
            },
            error: function(){ alert('錯誤') }
        });
    });
// song add queue
    $('li.song-add-queue').on('click', function(){
        var $this = $(this),
            id = (song_id != null) ? song_id : $this.closest(selector).data('id');
        $.ajax({
            type: "GET",
            'url': urlPlayqueueSongAppend(id),
            dataType: "html",
            success : function(data){
                $(data).appendTo(audioplayer.playQueue);
                $this.parent().css('visibility', 'hidden');
                if (audioplayer.playQueue.find('li.active').length == 0) {
                    audioplayer.playQueue.children().first()
                                         .find('i.queue-play-btn').trigger('click');
                }
            },
            error: function(){ alert('錯誤') }
        });
    });
// song add playlist
    $('li.song-add-playlist').on('click', function(e){
        var $this = $(this),
            $body = $('body'),
            id = (song_id != null) ? song_id : $this.closest(selector).data('id');

        $this.parent().css('visibility', 'hidden');

        $.ajax({
            type: "GET",
            'url': urlMusicPlaylistAdd('song', id),
            success: function(data, string, xhr){
                if (xhr.status == 278) {
                    var url = xhr.getResponseHeader('Location'),
                        pos = url.indexOf('?next='),
                        redirect_url = url.slice(0, pos+6) + window.location.pathname;
                    $.get(redirect_url, function(data){
                        dataAjaxLoad(data, redirect_url);
                    })
                }
                else {
                    $('<div></div>', { 'id': 'popout-black-cover' }).prependTo($body);
                    $('<div></div>', { 'id': 'fixed-center' }).html(data).prependTo($body);
                    popOutActivate(urlMusicPlaylistAdd('song', id));
                }
            },
        });
    });
}

// id is binded on selector
var ajaxAlbumUtilsSet = function(album_id, selector, csrf_token, prefix){
// album-like-btn
    $('i.'+ prefix +'-like-btn').on('click', function(){
        var $this = $(this),
            like_num = parseInt($this.text()),
            action = $this.hasClass('fa-heart-o') ? 'like': 'unlike',
            id = (album_id != null) ? album_id : $this.closest(selector).data('id');

        $.ajax({
            type: "POST",
            headers: {'X-CSRFToken': csrf_token},
            url: urlMusicAlbumLike,
            data: {
                'album_id': id,
                'action': action,
            },
            success : function(data, string, xhr){
                var content_type = xhr.getResponseHeader('Content-Type');
                if (xhr.status == 278) {
                    var url = xhr.getResponseHeader('Location'),
                        pos = url.indexOf('?next='),
                        redirect_url = url.slice(0, pos+6) + window.location.pathname;
                    $.get(redirect_url, function(data){
                        dataAjaxLoad(data, redirect_url);
                    })
                }
                else {
                    if (action == 'like') {
                        $this.removeClass('fa-heart-o').addClass('fa-heart red')
                                                       .text(' ' + (like_num+1));
                    }
                    else {
                        $this.removeClass('fa-heart red').addClass('fa-heart-o')
                                                       .text(' ' + (like_num-1));
                    }
                }
            },
            error: function(){ alert('錯誤') }
        });
    });

// album add queue
    $('li.'+ prefix +'-add-queue').on('click', function(){
        var $this = $(this),
            id = (album_id != null) ? album_id : $this.closest(selector).data('id');

        $.ajax({
            type: "GET",
            'url': urlPlayqueueAlbumAppend(id),
            dataType: "html",
            success : function(data){
                $(data).appendTo(audioplayer.playQueue);
                $this.parent().css('visibility', 'hidden');
                if (audioplayer.playQueue.find('li.active').length == 0) {
                    audioplayer.playQueue.children().first()
                                         .find('i.queue-play-btn').trigger('click');
                }
            },
            error: function(){ alert('錯誤') }
        });
    });

// album add playlist
    $('li.'+ prefix +'-add-playlist').on('click', function(e){
        var $this = $(this),
            $body = $('body'),
            id = (album_id != null) ? album_id : $this.closest(selector).data('id');

        $this.parent().css('visibility', 'hidden');

        $.ajax({
            type: "GET",
            'url': urlMusicPlaylistAdd('album', id),
            success: function(data, string, xhr){
                if (xhr.status == 278) {
                    var url = xhr.getResponseHeader('Location'),
                        pos = url.indexOf('?next='),
                        redirect_url = url.slice(0, pos+6) + window.location.pathname;
                    $.get(redirect_url, function(data){
                        dataAjaxLoad(data, redirect_url);
                    })
                }
                else {
                    $('<div></div>', { 'id': 'popout-black-cover' }).prependTo($body);
                    $('<div></div>', { 'id': 'fixed-center' }).html(data).prependTo($body);
                    popOutActivate(urlMusicPlaylistAdd('album', id));
                }
            },
        });
    });
}

// id is binded on selector
var ajaxPlaylistUtilsSet = function(playlist_id, selector, csrf_token, prefix){
// playlist-like-btn
    $('i.'+ prefix +'-like-btn').on('click', function(){
        var $this = $(this),
            like_num = parseInt($this.text()),
            action = $this.hasClass('fa-heart-o') ? 'like': 'unlike',
            id = (playlist_id != null) ? playlist_id : $this.closest(selector).data('id');

        $.ajax({
            type: "POST",
            headers: {'X-CSRFToken': csrf_token },
            url: urlMusicPlaylistLike,
            data: {
                'playlist_id': id,
                'action': action,
            },
            success : function(data, string, xhr){
                var content_type = xhr.getResponseHeader('Content-Type');
                if (xhr.status == 278) {
                    var url = xhr.getResponseHeader('Location'),
                        pos = url.indexOf('?next='),
                        redirect_url = url.slice(0, pos+6) + window.location.pathname;
                    $.get(redirect_url, function(data){
                        dataAjaxLoad(data, redirect_url);
                    })
                }
                else {
                    if (action == 'like') {
                        $this.removeClass('fa-heart-o').addClass('fa-heart red')
                                                       .text(' ' + (like_num+1));
                    }
                    else {
                        $this.removeClass('fa-heart red').addClass('fa-heart-o')
                                                       .text(' ' + (like_num-1));
                    }
                }
            },
            error: function(){ alert('錯誤') }
        });
    });

// playlist append queue
    $('li.'+ prefix +'-add-queue').on('click', function(){
        var $this = $(this),
            id = (playlist_id != null) ? playlist_id : $this.closest(selector).data('id');

        $.ajax({
            type: "GET",
            'url': urlPlayqueuePlaylistAppend(id),
            dataType: "html",
            success : function(data){
                $(data).appendTo(audioplayer.playQueue);
                $this.parent().css('visibility', 'hidden');
                if (audioplayer.playQueue.find('li.active').length == 0) {
                    audioplayer.playQueue.children().first()
                                         .find('i.queue-play-btn').trigger('click');
                }
            },
            error: function(){ alert('錯誤') }
        });
    });

// playlist add playlist
    $('li.'+ prefix +'-add-playlist').on('click', function(e){
        var $this = $(this),
            $body = $('body'),
            id = (playlist_id != null) ? playlist_id : $this.closest(selector).data('id');

        $this.parent().css('visibility', 'hidden');

        $.ajax({
            type: "GET",
            'url': urlMusicPlaylistAdd('playlist', id),
            success: function(data, string, xhr){
                if (xhr.status == 278) {
                    var url = xhr.getResponseHeader('Location'),
                        pos = url.indexOf('?next='),
                        redirect_url = url.slice(0, pos+6) + window.location.pathname;
                    $.get(redirect_url, function(data){
                        dataAjaxLoad(data, redirect_url);
                    })
                }
                else {
                    $('<div></div>', { 'id': 'popout-black-cover' }).prependTo($body);
                    $('<div></div>', { 'id': 'fixed-center' }).html(data).prependTo($body);
                    popOutActivate(urlMusicPlaylistAdd('playlist', id));
                }
            },
        });
    });
}