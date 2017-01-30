(function(){
// dropdown menu auto-close
    $('body').on('click', 'ul.dropdown-menu a', function(){
        $(this).closest('ul.dropdown-menu').hide();
    })

// user icon
    $('div#nav').on('click', 'img#user-icon', function(e){
        var $playerWrapper = $('#player-wrapper'),
            $playQueueWrapper = $playerWrapper.find('div#play-queue-wrapper');
        if (!$playerWrapper .is(':hidden')) {
            if (!$playQueueWrapper.is(':hidden')) {
                $playQueueWrapper.slideUp('200').promise().done(WrapperUp);
                function WrapperUp() {
                    $playerWrapper .slideUp('200');
                }
            }
            else {
                $playerWrapper.slideUp('300');
            }
        }
        $('ul.dropdown-menu').toggle();
        e.preventDefault();
    });

// player handle
    $('a#player-handle').on('click', function(e){
        if (!$('ul.dropdown-menu').is('hidden')) {
            $('ul.dropdown-menu').hide();
        }
        $('#player-wrapper').slideToggle('300');
        e.preventDefault();
    });

    $('i#list-button').on('click', function(){
        $('div#play-queue-wrapper').slideToggle('300');
    });

// play-queue hover effect
    $('ul#play-queue').on('mouseenter', "li", function(){
        var $this = $(this);
        $this.find('i.play-song').show();
        $this.find('div.close-wrapper').show();
    }).on('mouseleave', "li", function(){
        var $this = $(this);
        $this.find('i.play-song').hide();
        $this.find('div.close-wrapper').hide();
    });

// trash-can effect
    $('div.list-header i.fa-trash-o').hover(function(){
        $(this).siblings().toggle();
    });

// handle 'a' href AJAX way
    $(document).on('click', 'a', function(e){
        var href  = this.href,
            $container = $('div#container'),
            $script = $('script#main'),
            ori_title = document.title,
            ori_url = document.location.href;

    // do nothing if logout or href == '#'
        if ( !(href.slice(-1) == '#') ){
            e.preventDefault();

            $.ajax({
                type: "GET",
                url: href,
                success: function(data, string, xhr){
                    if (xhr.status == 278) {
                        var url = xhr.getResponseHeader('Location');
                        $.get(url, function(data){
                            dataAjaxLoad(data, url);
                        })
                    }
                    else {
                        dataAjaxLoad(data, href)
                    }
                },
            });
        }
    });

// popstate event handle prev/forward page btn
    window.onpopstate = function(e){
        if(e.state){
            var $container = $('div#main-wrapper');
            $container.html(e.state.html);
            $('script#main').html(e.state.script);
            document.title = e.state.title;
            eval(e.state.script);
        }
    };

// handle all forms AJAX way
    $(document).on('submit', 'form', function(e){
        var formData = new FormData(this),
            url = this.action,
            method = this.method;
        // action == '#' already handle AJAX WAY, if user use login-form we refresh
        if (this.action.slice(-1) == '#' || this.getAttribute('id') == 'login-form'){
            return;
        }

        e.preventDefault();
        // disable the submit button to prevent re-submit
        $(this).find('button[type=submit]').prop('disabled',true);

        if (method == "post") {
            $.ajax({
                type: method,
                'url': url,
                data: formData,
                processData: false,
                contentType: false,
                success: function(data, string, xhr){
                    if (xhr.status == 278) {
                        var url = xhr.getResponseHeader('Location');
                        $.get(url, function(data){
                            dataAjaxLoad(data, url);
                        })
                    }
                    else {
                        dataAjaxLoad(data, url);
                    }
                }
            });
        }
    // GET method not work with formData, probably request.GET can't deal with it
        else {
            $.ajax({
                type: method,
                'url': url,
                data: $(this).serialize(),
                success: function(data, string, xhr){
                    dataAjaxLoad(data, this.url);
                }
            });
        }
    });
})();



