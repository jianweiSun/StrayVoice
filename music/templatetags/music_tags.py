from django import template

register = template.Library()


@register.inclusion_tag('music/manage/album_bar.html')
def show_albums_bar(all_albums, album=None):
    return {'all_albums': all_albums,
            'album': album}


@register.simple_tag
def get_genre_name(genre_code):
    if genre_code == 'all':
        return '全部類型'
    else:
        GENRE_CHOICES = [(0, '未分類曲風'),
                         (1, 'Hip hop/ Rap'),
                         (2, 'Rock'),
                         (3, 'R&B/ Soul'),
                         (4, 'Singer/ Songwriter')]
        genre_dict = dict(GENRE_CHOICES)
        return genre_dict[int(genre_code)]


@register.inclusion_tag('music/user_side_bar.html')
def show_user_side_bar(request, obj):
    return {'object': obj,
            'request': request}


@register.simple_tag
def get_order_type_name(type_iter):
    type_dict = {'latest': '最新上傳', 'most_liked': '最多喜歡',
                 'recent_liked': '近期喜歡', 'recent_followed': '近期追蹤'}
    return type_dict[type_iter]

