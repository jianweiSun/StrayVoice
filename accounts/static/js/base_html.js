(function(){

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

})();



