# -*- coding: utf-8 -*-
#

from adminpage.views import *
from django.conf.urls import url

__author__ = "Epsirom"


urlpatterns = [
    url(r'^login/?$',adminLogin.as_view()),
    url(r'^logout/?$',adminLogout.as_view()),
    url(r'^activity/list/?$',activityList.as_view()),
    url(r'^activity/create/?$',activityCreate.as_view()),
    url(r'^activity/delete/?$',activityDelete.as_view()),
    url(r'^image/upload/?$',imageUpload.as_view()),
    url(r'^activity/detail/?$',activityDetail.as_view()),
    url(r'^activity/menu/?$',activityMenu.as_view()),
    url(r'^activity/checkin/?$',activityCheckin.as_view()),
]
