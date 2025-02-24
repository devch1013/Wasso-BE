from django.contrib import admin
from .models import Event, Attendance, Notice, AbsentApply

admin.site.register(Event)
admin.site.register(Attendance)
admin.site.register(Notice)
admin.site.register(AbsentApply)
