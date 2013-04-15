from django.contrib import admin
from  models import *

classes = [MobileDevice, PushMessage]
for cls in classes:
    admin.site.register(cls)
