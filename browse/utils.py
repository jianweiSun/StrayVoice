from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def queryset_paging(request, queryset, num):
    queryset_paginator = Paginator(queryset, num)
    page = request.GET.get('page')
    try:
        queryset = queryset_paginator.page(page)
    except PageNotAnInteger:
        queryset = queryset_paginator.page(1)
    except EmptyPage:
        queryset = queryset_paginator.page(queryset_paginator.num_pages)
    return queryset
