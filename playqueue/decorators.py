from django.http import HttpResponseBadRequest


def ajax_required(func):
    def wrapper_function(request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest()
        return func(request, *args, **kwargs)
    wrapper_function.__doc__ = func.__doc__
    wrapper_function.__name__ = func.__name__
    return wrapper_function
