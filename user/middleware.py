from django.http import HttpResponseForbidden

class CookieCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check for the cookie
        if request.path != '/rss/init' and ('tokendt' not in request.COOKIES or request.COOKIES['tokendt'] != 'caoDt.'):
            return HttpResponseForbidden("请登录")

        # If the cookie is present, continue processing the request
        response = self.get_response(request)
        return response