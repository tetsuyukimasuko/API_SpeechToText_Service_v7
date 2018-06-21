from django.contrib import admin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.admin import UserAdmin
from .models import User, Organization,ConferenceList, ConferenceLog

class UserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class UserAdmin(UserAdmin):
    form = UserChangeForm
    fieldsets = (
        (None, {'fields': ('username','first_name','last_name','password','email','org','user_permissions','is_active','last_login','date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
    list_display = ('username','email','org')
    list_filter = ('org', 'is_staff')
    search_fields = ('username', 'email')
    ordering = ('org', )
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
admin.site.register(Organization)
admin.site.register(ConferenceList)
admin.site.register(ConferenceLog)