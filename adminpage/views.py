from django.shortcuts import render
from django.contrib import auth
from codex.baseerror import *
from codex.baseview import *

# Create your views here.

class adminLogin(APIView):
    def get(self):
        if not self.request.user.is_authenticated():
            raise ValidateError(self.input)

    def post(self):
        self.check_input('username', 'password')
        username = self.input['username']
        password = self.input['password']
        try:
            user = auth.authenticate(username=username,password=password)
            if not user:
                raise ValidateError("user does not exit!")
            auth.login(self.request, user)
        except:
            raise ValidateError("Fail to login!")

class adminLogout(APIView):
    def post(self):
        try:
            auth.logout(self.request)
        except:
            raise ValidateError("Fail to logout!")