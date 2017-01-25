from django.http import HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin


class AjaxRedirectMiddleware(MiddlewareMixin):

    def process_response(self, request, response):
        if request.is_ajax():
            if type(response) == HttpResponseRedirect:
                response.status_code = 278
        return response
