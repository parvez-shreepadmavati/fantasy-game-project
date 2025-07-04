from django.contrib import admin
from django.contrib.auth import get_user_model
from datetime import timedelta

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from drf_secure_token.models import Token
# from import_export.admin import ExportActionMixin
# from import_export.formats import base_formats

# Register your models here.


User = get_user_model()

# admin.site.unregister(Group)
# admin.site.unregister(Token)


def make_active(modeladmin, request, queryset):
    for item in queryset:
        item.is_active = True
        item.save()

def make_inactive(modeladmin, request, queryset):
    for item in queryset:
        item.is_active = False
        item.save()


@admin.register(User)
class UserAdmin(UserAdmin):
    """
    for user module in admin
    """

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
    fieldsets = (
        ('Personal info', {'fields': ('uuid', 'username', 'email', 'date_of_birth',)}),
        ('Status', {'fields': ('is_active',)}),
        # ('Service', {'fields': ('is_staff', 'is_superuser', 'user_permissions',)}),  # 'groups', 'user_permissions'
        ('Account dates', {'fields': ('date_joined', 'last_login', 'last_user_activity', 'last_modified',)}),

    )
    readonly_fields = ('uuid', 'last_modified')
    list_display = ('uuid', 'username','email', 'date_of_birth', 'date_joined',)
    search_fields = ('username', 'email', 'uuid')
    actions = [make_active, make_inactive]

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term != '':
            queryset |= self.model.objects.filter(username=search_term)

        return queryset, use_distinct