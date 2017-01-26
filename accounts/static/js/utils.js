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