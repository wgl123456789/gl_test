import jwt
from datetime import datetime,timedelta
from django.conf import settings
from django.http import JsonResponse
from rest_framework.authentication import BaseAuthentication,get_authorization_header
from rest_framework import exceptions
from django.contrib.auth import get_user_model
from jwt.exceptions import ExpiredSignatureError
MTUser = get_user_model()

def generate_jwt(user):
    expire_time = datetime.now() + timedelta(days=7)
    return jwt.encode({"userid":user.pk,"exp":expire_time},key=settings.SECRET_KEY).decode('utf-8')


class JWTAuthentication(BaseAuthentication):
    keyword = 'JWT'
    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = "不可用的JWT请求头！"
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = '不可用的JWT请求头！JWT Token中间不应该有空格！'
            raise exceptions.AuthenticationFailed(msg)

        try:
            jwt_token = auth[1]
            jwt_info = jwt.decode(jwt_token,settings.SECRET_KEY)
            userid = jwt_info.get('userid')
            try:
                # 绑定当前user到request对象上
                user = MTUser.objects.get(pk=userid)
                return user, jwt_token
            except:
                msg = '用户不存在！'
                raise exceptions.AuthenticationFailed(msg)
        except ExpiredSignatureError:
            msg = "JWT Token已过期！"
            raise exceptions.AuthenticationFailed(msg)



