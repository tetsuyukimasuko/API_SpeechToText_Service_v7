from rest_framework import serializers
from .models import User, Organization, ConferenceList,ConferenceLog


#ユーザー情報のシリアライザー
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','password', 'username', 'email','org')
        write_only_fields = ('password',)
        read_only_fields = ('is_staff', 'is_superuser', 'is_active', 'date_joined',)
 
    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


#組織情報のシリアライザー
class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model=Organization
        fields="__all__"

#会議情報のシリアライザー
class ConferenceInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model=ConferenceList
        fields="__all__"

#会議ログのシリアライザー
class ConferenceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model=ConferenceLog
        fields=('timestamp','speaker_name','text',)

