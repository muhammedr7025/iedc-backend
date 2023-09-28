import uuid
from datetime import timedelta
import random

import decouple
from django.db.models import Q
from rest_framework.views import APIView
from utils.response import CustomResponse

from dashboard.serializer import UserRegisterSerializer
from .models import User, ForgetPassword, Role, Group
from utils.utils import DateTimeUtils
from django.core.mail import send_mail
from rest_framework.permissions import AllowAny
permission_classes = (AllowAny,)


class UserRegisterAPI(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):

        roles = Role.objects.all()

        if roles.exists():
            random_role = random.choice(
                roles
            )

        serializer = UserRegisterSerializer(
            data=request.data,
            context={
                'role': random_role
            }
        )

        if serializer.is_valid():
            serializer.save()

            return CustomResponse(
                general_message='User created successfully'
            ).get_success_response()

        return CustomResponse(
            response=serializer.errors
        ).get_failure_response()


class UserLoginAPI(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):

        email_muid = request.data.get('emailOrMuid')
        password = request.data.get('password')

        user = User.objects.filter(
            Q(muid=email_muid) |
            Q(email=email_muid)
        ).first()

        if user:
            if user.check_password(password):
                return CustomResponse(
                    general_message='Successfully login'
                ).get_success_response()
            else:
                return CustomResponse(
                    general_message='incorrect password'
                ).get_failure_response()

        return CustomResponse(
            general_message='invalid email or muid'
        ).get_failure_response()


class CreateBulkGroupsAPI(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        user_count = User.objects.all().count()
        group_count = user_count // 6 + 1
        groups = []
        for group_num in range(1, group_count):
            group = Group(
                id=uuid.uuid4(),
                title=f"group{group_num}",
                created_at=DateTimeUtils.get_current_utc_time()
            )
            groups.append(group)

        Group.objects.bulk_create(groups)

        return CustomResponse(
            general_message='Groups created successfully'
        ).get_success_response()


class ForgotPasswordAPI(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        email_muid = request.data.get('emailOrMuid')

        user = User.objects.filter(
            Q(muid=email_muid) |
            Q(email=email_muid)
        ).first()

        if user:
            user_verification_otp = ForgetPassword.objects.create(
                id=uuid.uuid4(),
                user=user,
                otp=random.randrange(00000, 99999, 6),
                expiry=DateTimeUtils.get_current_utc_time() + timedelta(seconds=600),
                created_at=DateTimeUtils.get_current_utc_time()
            )

            send_mail(
                subject='Forget Password',
                message=f'This is your otp {user_verification_otp.otp}',
                from_email=decouple.config("FROM_MAIL"),
                recipient_list=[user.email]
            )

            return CustomResponse(
                general_message='User verification OTP send successfully'
            ).get_success_response()

        else:
            return CustomResponse(
                general_message='Invalid muid or mails'
            ).get_failure_response()