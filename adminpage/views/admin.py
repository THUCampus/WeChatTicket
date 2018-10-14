from codex.baseerror import *
from codex.baseview import APIView

from django.contrib.auth import authenticate, login, logout


class AdminLogin(APIView):

    def validate_user(self):
        username = self.input['username']
        password = self.input['password']
        user = authenticate(username=username, password=password)
        if user is None:
            raise ValidateError(self.input)
        else:
            try:
                login(self.request, user)
            except Exception as e:
                raise AuthError(self.input)

    def get(self):
        if not self.request.user.is_authenticated():
            raise ValidateError(self.input)

    def post(self):
        self.check_input('username', 'password')
        self.validate_user()


class AdminLogout(APIView):

    def post(self):
        if not self.request.user:
            raise ValidateError(self.input)
        else:
            try:
                logout(self.request)
            except Exception as e:
                raise AuthError(self.input)