from rest_framework import permissions
from .models import ConferenceList
 
 #管理者およびインスタンスに紐づくユーザーしかアクセスできない
 #https://richardtier.com/2014/02/25/django-rest-framework-user-endpoint/
class IsStaffOrTargetUser(permissions.BasePermission):
    def has_permission(self, request, view):
        # allow user to list all users if logged in user is staff
        return view.action == 'retrieve' or request.user.is_staff
 
    def has_object_permission(self, request, view, obj):
        # allow logged in user to view own details, allows staff to view all records
        return request.user.is_staff or obj == request.user

#管理者しかアクセスできない
#http://racchai.hatenablog.com/entry/2016/05/27/070000
class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        
        return request.user and request.user.email == 'bigdata@change-jp.com'

#当該辞書を保有する組織に所属するユーザーしかアクセスできない
class IsStaffOrTargetDict(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False

        org_id=request.parser_context['kwargs']['org_id']
        return str(request.user.org_id) == org_id or request.user.is_staff
 
#当該会議の開催されている組織に所属するユーザーしかアクセスできない
class IsStaffOrTargetConf(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False

        conf_id=request.parser_context['kwargs']['conf_id']
        try:
            c=ConferenceList.objects.get(pk=conf_id)
            org_id=c.org_id
        except:
            org_id=None

        # allow user to list all users if logged in user is staff
        return request.user.org == org_id or request.user.is_staff

#当該組織に所属するユーザーしかアクセスできない
class IsStaffOrTargetOrg(permissions.BasePermission):
    def has_permission(self, request, view):
        # allow user to list all users if logged in user is staff
        return view.action == 'retrieve' or request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if request.user.is_anonymous:
            return False

        # allow logged in user to view own details, allows staff to view all records
        return request.user.is_staff or obj.org_id == request.user.org


