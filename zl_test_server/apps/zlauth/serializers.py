from rest_framework import serializers
from django.contrib.auth import get_user_model

ZLUser = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZLUser
        fields = ['uid','telephone','username','email','avatar','date_joined','is_active']