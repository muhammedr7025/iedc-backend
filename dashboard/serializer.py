from rest_framework import serializers
import uuid
from .models import User, UserRoleLink, Group
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
        validated_data['created_at'] = DateTimeUtils.get_current_utc_time()
        validated_data['is_active'] = False

        user = User.objects.create(**validated_data)

        user_role_link = {
            'id': uuid.uuid4(),
            'user': user,
            'role': self.context.get('role'),
            'created_at': DateTimeUtils.get_current_utc_time()
        }

        UserRoleLink.objects.create(**user_role_link)

        return user

    def validate_password(self, password):
        if password == self.initial_data.get('confirm_password'):
            return make_password(password)
        raise serializers.ValidationError("Passwords does not match")


# class CreateBulkGroupsSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = Group
#         fields = []
#
#         def create(self, validated_data):
#             groups = []
#             for group in range(5):
#                 validated_data['id'] = uuid.uuid4()
#                 validated_data['title'] = f"group{group}"
#                 validated_data['created_at'] = DateTimeUtils.get_current_utc_time()
#
#                 groups.append(**validated_data)
#
#             return Group.objects.bulk_create(groups)
