from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import models as auth_models
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django_celery_beat import admin as celery_beat_admin
from django_celery_beat import models as celery_beat_models
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm


class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm


REGISTER = {
    auth_models.User: UserAdmin,
    auth_models.Group: auth_admin.GroupAdmin,
    celery_beat_models.PeriodicTask: celery_beat_admin.PeriodicTaskAdmin,
    celery_beat_models.ClockedSchedule: celery_beat_admin.ClockedScheduleAdmin,
    celery_beat_models.CrontabSchedule: celery_beat_admin.CrontabScheduleAdmin,
    celery_beat_models.SolarSchedule: None,
    celery_beat_models.IntervalSchedule: None,
}

for model, model_admin in REGISTER.items():
    admin.site.unregister(model)

    if model_admin:

        class UnfoldAdmin(model_admin, ModelAdmin):
            pass

        admin.site.register(model, UnfoldAdmin)
    else:
        admin.site.register(model, ModelAdmin)
