from rest_framework import serializers
import uuid
from .models import User
from utils.utils import DateTimeUtils
from django.contrib.auth.hashers import make_password


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
            'muid',
            'email',
            'phone',
            'password',
        ]

    def create(self, validated_data):
        validated_data['id'] = str(uuid.uuid4())
        validated_data['qr_code'] = str(uuid.uuid4())
        validated_data['is_active'] = True
        validated_data['created_at'] = DateTimeUtils.get_current_utc_time()

        return User.objects.create_user(**validated_data)

    def validate_password(self, password):
        if password == self.initial_data.get('confirm_password'):
            return password
        raise serializers.ValidationError("Passwords does not match")
