from rest_framework import routers
from .views import UserViewSet, OrganizationViewSet, CustomModelViewSet,ConferenceLogViewSet,ConferenceViewSet,OrganizationMemberViewSet, LoginViewSet, UserRegisterViewSet
from django.conf.urls import include, url


router=routers.DefaultRouter()
router.register(r'^login',LoginViewSet)
router.register(r'^users',UserViewSet)
#router.register(r'^users/(?P<user_id>\w{8}-\w{4}-\w{4}-\w{4}-\w{12})/register',UserRegisterViewSet)
router.register(r'^orgs',OrganizationViewSet)
router.register(r'^conferences',ConferenceViewSet)
router.register(r'^conferences/(?P<conf_id>\w{8}-\w{4}-\w{4}-\w{4}-\w{12})/log',ConferenceLogViewSet)
router.register(r'^orgs/(?P<org_id>\w{8}-\w{4}-\w{4}-\w{4}-\w{12})/dict',CustomModelViewSet)
router.register(r'^orgs/(?P<org_id>\w{8}-\w{4}-\w{4}-\w{4}-\w{12})/member',OrganizationMemberViewSet)


