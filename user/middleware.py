import os

from django.http import HttpResponseForbidden
from django.utils.timezone import now as timezone_now
import hashlib
from dotenv import load_dotenv

load_dotenv()

class CookieCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def generate_hash(self, input_string):
        today_str = timezone_now().strftime('%Y-%m-%d')
        salted_input = input_string + today_str
        hash_object = hashlib.sha256()
        hash_object.update(salted_input.encode('utf-8'))
        hash_hex = hash_object.hexdigest()
        return hash_hex

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        return ip

    def __call__(self, request):
        ip = self.get_client_ip(request)

        response = self.get_response(request)
        if request.path == os.environ['WHITE_LIST_API_1'] or request.path == os.environ['WHITE_LIST_API_5']:
            return response

        if ip == '127.0.0.1' and (request.path == os.environ['WHITE_LIST_API_2'] or request.path == os.environ['WHITE_LIST_API_3'] or request.path == os.environ['WHITE_LIST_API_4']):
            return response

        if 'tokendt' not in request.COOKIES:
            return HttpResponseForbidden("请登录")

        else:
            cookie_value = request.COOKIES[os.environ['COOKIE_NAME']]
            target_value = self.generate_hash(os.environ['SALT'])
            if cookie_value != target_value:
                return HttpResponseForbidden("请登录")

        return response
