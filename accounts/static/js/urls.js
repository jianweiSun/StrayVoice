var urlMusicSongLike = "/music/song_like/";

var urlMusicPlaylistAdd = function(type, song_id){
    return "/music/playlist/" + type + '/' + song_id + '/add/'
}


var urlPlayqueueSongPrepend = function(song_id){
    return "/playqueue/song/" + song_id + "/prepend/"
}

var urlPlayqueueSongAppend = function(song_id){
    return "/playqueue/song/" + song_id + "/append/"
}

