function AudioPlayer(container) {
	this.container = container;
	this.audio = this.container.find('audio')[0];
	this.playButton = this.container.find('#play-button'); 
	this.forwardButton = this.container.find('#forward-button'); 
	this.backwardButton = this.container.find('#backward-button'); 
	this.repeatButton = this.container.find('#repeat-button');
	this.listButton = this.container.find('#list-button');
	this.volumnButton = this.container.find('#volume-button');
	this.currentTime = this.container.find('#current-time');
	this.fullDuration = this.container.find('#full-duration');
	this.barWrapper = this.container.find('#bar-wrapper');
	this.progressBar = this.container.find('#progress-bar');
	this.bufferedBar = this.container.find('#buffered-bar');
	this.volumnControl = this.container.find('#volume-control');
	this.playQueue = this.container.find('#play-queue');
	this.playingSongData = this.container.find('#playing-data-wrapper');

	this.init();
}

AudioPlayer.prototype.init = function(){
	var self = this;
	this.playButton.on('click', $.proxy(this.playOrPause, this));
	this.volumnSet();
	this.queuePlayButtonSet();
	this.forwardButtonSet();
	this.backwardButtonSet();
	this.repeatButtonSet();
	this.autoFetchNext();
	this.queueCloseButtonSet();
	this.queueClearButtonSet();
	this.likeButtonSet();
	// trigger the first song
    this.playQueue.find('li:first').find('i.queue-play-btn').trigger('click');
    // avoid race condition between pause() and play()
    setTimeout(function(){
        self.playQueue.find('li:first').find('i.queue-play-btn').trigger('click');
    }, 300);
}

AudioPlayer.prototype.song_init = function($song_li){
    var dfd = $.Deferred(),
        src = $song_li.data('src'),
        self = this;
    // load data into bar
    $song_li.find('div.close-wrapper').remove();
    $song_li.find('i.queue-play-btn').remove();
    $song_li.find('div.like-wrapper').append();

    this.playingSongData.html('').append($song_li);

    // load source
    $(this.audio).find('source').attr('src', src);
    this.audio.load();

    // init button
    this.audio.addEventListener('loadedmetadata', function(){
		self.timeUpdate();
		self.barUpdate();
		self.barWrapper.on('click', $.proxy(self.setNewTime, self));
		dfd.resolve();
	});

    return dfd.promise();
}

AudioPlayer.prototype.playOrPause = function(e){
	var unactive = 'queue-play-btn play-song fa fa-play-circle-o fa-3x',
        active_play = 'queue-play-btn div-center fa fa-pause-circle fa-3x queue-playing',
        active_pause = 'queue-play-btn div-center fa fa-play-circle fa-3x queue-playing',
        $queue_btn = this.playQueue.find('li.active i.queue-play-btn');

    e.preventDefault();

    if (this.audio.paused) {
        this.audio.play();
        this.playButton.removeClass('fa-play')
                       .addClass('fa-pause');
        $queue_btn.removeClass().addClass(active_play);
    }
    else {
        this.audio.pause();
        this.playButton.removeClass('fa-pause')
                       .addClass('fa-play');
        $queue_btn.removeClass().addClass(active_pause);

    }
}

AudioPlayer.prototype.timeUpdate = function() {
	var self = this,
		duration = this.audio.duration, 
		minutes = Math.floor(duration / 60), 
		seconds = Math.round(duration % 60), 
		pad = function(num) {
			return (num < 10) ? '0' + num.toString() : num.toString();
		};
	
	this.fullDuration.html(pad(minutes) + ':' + pad(seconds));

	this.audio.addEventListener('timeupdate', function(){
		var current = this.currentTime,
			minutes = Math.floor(current / 60), 
			seconds = Math.round(current % 60);

		self.currentTime.html(pad(minutes) + ':' + pad(seconds));
	});
};

AudioPlayer.prototype.barUpdate = function (){
	var self = this;

	this.audio.addEventListener('timeupdate', function(){
		// progress bar parts
		var progressSizeNum = (this.currentTime/this.duration * 100);
		self.progressBar.css('width', progressSizeNum + '%');
		// buffer bar parts
		if (this.buffered.length > 0) {
            var bufferedTime = this.buffered.end(0) - this.buffered.start(0),
                bufferedSizeNum = (bufferedTime / this.duration * 100);
            self.bufferedBar.css('width', bufferedSizeNum + '%');
	    }
	});
};

AudioPlayer.prototype.setNewTime = function (e) {
	var mouseX = e.pageX, 
		windowSize = $(window).width(), 
		newTime = ( mouseX/windowSize * this.audio.duration);
	this.audio.currentTime = newTime;
}

AudioPlayer.prototype.volumnSet = function() {
	var self = this;
	this.volumnButton.on('click', function(){
		self.volumnControl.toggle();
	});
	this.volumnControl.on('change', function(){
		self.audio.volume = parseFloat(this.value/100);

		if (parseFloat(this.value/100) == 0) {
			self.volumnButton.attr('class', 'fa fa-volume-off');
		}
		else if (parseFloat(this.value/100) < 0.5) { 
			self.volumnButton.attr('class', 'fa fa-volume-down');
		}
		else {
			self.volumnButton.attr('class', 'fa fa-volume-up');
		}
	});
}

// the main function logic to trigger others
AudioPlayer.prototype.queuePlayButtonSet = function() {
    var self = this,
        unactive = 'queue-play-btn play-song fa fa-play-circle-o fa-3x',
        active_play = 'queue-play-btn div-center fa fa-pause-circle fa-3x queue-playing',
        active_pause = 'queue-play-btn div-center fa fa-play-circle fa-3x queue-playing';

    // queue-play-btn set
    this.playQueue.on('click', 'i.queue-play-btn', function(){
        var $this = $(this),
            $li = $this.closest('li');
            $li_to_pass = $this.closest('li').clone(true);
            $active = self.playQueue.find('li.active');

        switch($this.prop('class')) {
            case unactive:
                // if there's song active, un-active it
                if ($active.length) {
                    $active.removeClass()
                           .find('i.queue-play-btn')
                           .removeClass().addClass(unactive).hide()
                           .siblings('img').show();
                }
                // active the song
                $this.removeClass().addClass(active_play).show()
                     .siblings('img').hide();
                $li.addClass('active');
                // clone the li then pass in to playing-data
                self.song_init($li_to_pass)
                     .done(function(){
                        self.playButton.trigger('click');
                     });
                break;
            case active_pause:
                $this.removeClass().addClass(active_play);
                self.playButton.trigger('click');
                break;
            case active_play:
                $this.removeClass().addClass(active_pause);
                self.playButton.trigger('click');
        }
    });
};

AudioPlayer.prototype.forwardButtonSet = function() {
    var self = this;
    this.forwardButton.on('click', function(){
       var $active = self.playQueue.find('li.active')
            next = $active.next(),
            first = self.playQueue.find('li').first(),
            length = self.playQueue.find('li').length;

        if (length == 1 && $active.length==1){
            return;
        }

        if (self.repeatButton.hasClass('fa-rotate-left')) {
            if (next.length) {
                next.find('i.queue-play-btn').trigger('click');
            }
            else {
                first.find('i.queue-play-btn').trigger('click');
            }
        }
        // if repeatButton is random, trigger random song
        else {
            self.utils_randomPickSong().find('i.queue-play-btn').trigger('click');
        }
    });
};

AudioPlayer.prototype.backwardButtonSet = function() {
    var self = this;
    this.backwardButton.on('click', function(){
       var  $active = self.playQueue.find('li.active'),
            prev = $active.prev(),
            last = self.playQueue.find('li').last();
            length = self.playQueue.find('li').length;

        if (length == 1 && $active.length==1){
            return;
        }

        if (self.repeatButton.hasClass('fa-rotate-left')) {
            if (prev.length) {
                prev.find('i.queue-play-btn').trigger('click');
            }
            else {
                last.find('i.queue-play-btn').trigger('click');
            }
        }
        // if repeatButton is random, trigger random song
        else {
            self.utils_randomPickSong().find('i.queue-play-btn').trigger('click');
        }
    });
};

AudioPlayer.prototype.repeatButtonSet = function() {
    this.repeatButton.on('click', function(){
        var $this = $(this);
        if ($this.hasClass('fa-rotate-left')) {
            $this.removeClass('fa-rotate-left').addClass('fa-random');
        }
        else {
            $this.removeClass('fa-random').addClass('fa-rotate-left');
        }
    });
};

AudioPlayer.prototype.autoFetchNext = function () {
    var self = this,
        active_pause = 'queue-play-btn div-center fa fa-play-circle fa-3x queue-playing';

    this.audio.addEventListener('ended', function(){
        var $all = self.playQueue.find('li'),
            $unactive = $all.not('li.active'),
            $queue_btn = self.playQueue.find('li.active i.queue-play-btn');
    // pause if only one song
        if (!$unactive.length) {
            self.playButton.removeClass('fa-pause')
                           .addClass('fa-play');
            $queue_btn.removeClass().addClass(active_pause);
            return;
        }

        if (self.repeatButton.hasClass('fa-rotate-left')) {
            self.forwardButton.trigger('click');
        }
        else {
            self.utils_randomPickSong().find('i.queue-play-btn').trigger('click');
        }
    });
};

AudioPlayer.prototype.utils_randomPickSong = function(){
    var self = this,
        $all = self.playQueue.find('li'),
        $unactive = $all.not('li.active'),
        random_index = Math.floor(Math.random() * $unactive.length);
    return $unactive.eq(random_index)
};

AudioPlayer.prototype.queueCloseButtonSet = function() {
    var self = this;

    this.playQueue.on('click', 'i.fa-close', function(){
        var $this = $(this),
            $li = $this.closest('li'),
            index = $li.index();

        $.ajax({
            type: "GET",
            url: "/playqueue/" + index + "/remove/",
            success : function() {
                if ($li.hasClass('active')) {
                    self.forwardButton.trigger('click');
                }
                $li.remove();
                // if clear all, make the audio pause
                if (!self.playQueue.find('li').length) {
                    if (!self.audio.paused) {
                        self.playButton.trigger('click');
                    }
                }
            },
            error: function(){ alert('錯誤') }
        });
    });
};

AudioPlayer.prototype.queueClearButtonSet = function() {
    var self = this;
    this.playQueue.parent().find('div.list-header i.fa-trash-o').on('click', function(){
        $.ajax({
            type: "GET",
            url: "/playqueue/clear/",
            success : function() {
                self.playQueue.empty();
                // if clear all, make the audio pause
                if (!self.audio.paused) {
                    self.playButton.trigger('click');
                }
            },
            error: function(){ alert('錯誤') }
        });
    });
};

 // bind the event to make btns on playqueue and now-playing song data work
AudioPlayer.prototype.likeButtonSet = function() {
    var self = this;
    this.container.on('click', 'i.queue-like-btn', function(){
        var $this = $(this),
            $li = $this.closest('li'),
            like_num = parseInt($this.text()),
            song_id = $li.data('id'),
            action = $this.hasClass('fa-heart-o') ? 'like': 'unlike';

        $.ajax({
            type: "POST",
            headers: {'X-CSRFToken': csrfToken },
            url: "/music/song_like/",
            data: {
                'song_id': song_id,
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
                    if ($li.hasClass('active') || $li.parent().is('#playing-data-wrapper')) {
                        var $btn_on_playing = self.container.find('ul#playing-data-wrapper i.queue-like-btn'),
                            $btn_on_queue = $active = self.playQueue.find('li.active i.queue-like-btn');

                        $this = $btn_on_playing.add($btn_on_queue);
                    }

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
};

var audioplayer = new AudioPlayer($('#player-wrapper'));

audioplayer.container.find('#icon-wrapper').on('click', 'a', function(e){
    e.preventDefault();
});