(function(){
// user icon and dropdown menu
    $('img#user-icon').on('click', function(e){
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

    $('ul.dropdown-menu a').on('click', function(){
        $(this).closest('ul.dropdown-menu').hide();
    })
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

// AJAX utility funciton
var


// handle 'a' href AJAX way
    $(document).on('click', 'a', function(e){
        var href  = this.href,
            location = document.location.href;
        // do nothing if logout or href == '#'
        if ( !(href.slice(-1) == '#') && !(href.endsWith('logout/')) ){
            var $container = $('div#container'),
                $script = $('script#main'),
                ori_title = document.title,
                ori_url = document.location.href;
            e.preventDefault();
            // create state obj for the first page( normal load without AJAX)
            if (history.state == null){
                history.replaceState(
                    {'html':$container.html(), 'script': $script.html(), 'title': ori_title},
                    ori_title,
                    ori_url
                )
            }

            $.ajax({
                type: "GET",
                'url': href,
                success: function(data, string, xhr){
                    var $data_div = $('<div></div>').html(data),
                        $content = $data_div.find('div#container'),
                        $script = $data_div.find('script#main'),
                        $title = $data_div.find('title');

                    $container.html($content.html());
                    $script.html($script.html());
                    document.title = $title.text();

                    eval($script.html());

                    history.pushState(
                        {'html':$container.html(), 'script': $script.html(), 'title': $title.text()},
                        $title.text(),
                        href
                    )
                },
            });
        }
    });
    window.onpopstate = function(e){
        if(e.state){
            $('div#container').html(e.state.html);
            $('script#main').html(e.state.script);
            document.title = e.state.title;
            eval(e.state.script);
        }
    };

})();



