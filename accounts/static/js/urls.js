var urlMusicSongLike = "/music/song_like/";

var urlMusicAlbumLike = "/music/album_like/";

var urlMusicPlaylistLike = "/music/playlist_like/";

var urlUserFollow = "/accounts/follow/";

var urlMusicPlaylistAdd = function(type, id){
    return "/music/playlist/" + type + '/' + id + '/add/'
}

var urlPlayqueueSongPrepend = function(song_id){
    return "/playqueue/song/" + song_id + "/prepend/"
}

var urlPlayqueueSongAppend = function(song_id){
    return "/playqueue/song/" + song_id + "/append/"
}

var urlPlayqueueAlbumAppend = function(album_id){
    return "/playqueue/album/" + album_id + "/append/"
}

var urlPlayqueuePlaylistAppend = function(playlist_id){
    return "/playqueue/playlist/" + playlist_id + "/append/"
}


