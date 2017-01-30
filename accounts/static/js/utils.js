// hard code selector = 'i.play-song'
var tableHoverEffect = function($row) {
    $row.hover(function(){
        $(this).css('background-color', '#e3e3e3')
               .find('i.play-song').show();
    }, function(){
        $(this).css('background-color', 'white')
               .find('i.play-song').hide();
    });
}

var popOutActivate = function(url){
    var $popOutDiv = $('div#fixed-center'),
        $popOutCover = $popOutDiv.next('#popout-black-cover'),
        cancelButton = $popOutDiv.find('button[type=button]'),
        form = $popOutDiv.find('form');

    cancelButton.on('click', function(){
        $popOutDiv.remove();
        $popOutCover.remove();
    });

    $('a.btn').on('click', function(){
        $popOutDiv.remove();
        $popOutCover.remove();
    })
    form.on('submit', function(e){
        $.ajax({
            type: "POST",
            'url': url,
            data: form.serialize(),
            success: function(data){
                $popOutDiv.remove();
                $popOutCover.remove();
            },
            error: function(){ alert('錯誤') }
        });
        e.preventDefault();
    });
};

// plus-btn toggle plus menu
var plusButtonToggleMenu = function(){
    $('i.fa-plus').on('click', function(){
        var $this = $(this),
            $menu = $this.siblings('ul.dropdown');

        if ($menu.css('visibility') == 'hidden') {
            $menu.css('visibility', 'visible');
        }
        else {
            $menu.css('visibility', 'hidden');
        }
    });
}

var tagClickSet = function(){
    $('div#tags a').on('click', function(e){
        var $this = $(this),
            tag = $(this).data('tag');
        $(this).parent('li').addClass('selected')
               .siblings().removeClass('selected');
        $('div[data-tag=' + tag + ']').show().siblings().hide();
        e.preventDefault();
    });
}

// img preview
var previewIMG = function(input) {
    if (input.files[0]) {
        var reader = new FileReader(),
            file = input.files[0];

        reader.readAsDataURL(file);

        reader.onload = function() {
            $('#img-preview').attr('src', reader.result);
        }
    }
};