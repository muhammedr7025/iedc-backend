import uuid
from datetime import timedelta
import random

from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
import decouple
from django.db import transaction
from django.db.models import Q, F
from rest_framework.views import APIView

from utils.permission import CustomizePermission, TokenGenerate
from utils.response import CustomResponse
from dashboard.serializer import UserRegisterSerializer
from .models import User, ForgetPassword, Role, Group, UserGroupLink, UserRoleLink
from utils.utils import DateTimeUtils
from django.core.mail import send_mail
from rest_framework.permissions import AllowAny
permission_classes = (AllowAny,)


class UserRegisterAPI(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):

        serializer = UserRegisterSerializer(
            data=request.data
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

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request, email=email, password=password)

        if user:
            auth = TokenGenerate().generate(user)
            return CustomResponse(response=auth).get_success_response()
        else:
            return CustomResponse(general_message="login failed").get_failure_response()


class UserProfileAPI(APIView):
    authentication_classes = [CustomizePermission]

    def get(self, request):
        user_id = request.data.get('user_id')

        user = User.objects.filter(
            id=user_id
        ).values(
            'username',
            'muid',
            role=F('user_role_link_user__role__title')
        )

        return CustomResponse(
            response=user
        ).get_success_response()


class QrCodeScannerAPI(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):

        user = request.user
        team_mate_qr_code = request.data.get('qr_code_id')
        user_id = request.data.get('user_id')

        team_mate_group = UserGroupLink.objects.filter(
            user__qr_code=team_mate_qr_code
        ).first()

        if team_mate_group is None:
            return CustomResponse(
                general_message='User has no group'
            ).get_failure_response()

        user_group = UserGroupLink.objects.filter(
            user__id=user_id
        ).first()

        if user_group is None:
            return CustomResponse(
                general_message='User has no group'
            ).get_failure_response()

        if user_group.group == team_mate_group.group:

            team_mate_details = User.objects.filter(
                id=team_mate_group.user.id
            ).values(
                'username',
                'muid',
                role=F(
                    'user_role_link_user__role__title'
                )
            )

            return CustomResponse(
                response=team_mate_details
            ).get_success_response()

        return CustomResponse(
            general_message='Opps! Connect another user'
        ).get_success_response()


class CreateBulkGroupsAPI(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        user_count = User.objects.all().count()

        if user_count % 6 != 0:

            remaining_users = 6 - (user_count % 6)

            return CustomResponse(
                general_message=f"Need {remaining_users} more users to assign group"
            ).get_failure_response()

        group_count = user_count // 6

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


class UserGroupLinkBulkCreateAPI(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        users = list(User.objects.all())
        groups = list(Group.objects.all())

        try:
            with transaction.atomic():
                for group in groups:

                    user_group = users[:6]
                    users = users[6:]
                    roles = list(Role.objects.all())

                    for index, user in enumerate(user_group):
                        role = roles[index]

                        UserGroupLink.objects.create(
                            id=uuid.uuid4(),
                            user=user,
                            group=group,
                            created_at=DateTimeUtils.get_current_utc_time()
                        )

                        UserRoleLink.objects.create(
                            id=uuid.uuid4(),
                            user=user,
                            role=role,
                            created_at=DateTimeUtils.get_current_utc_time()
                        )

        except Exception as e:
            return CustomResponse(
                general_message=str(e)
            ).get_failure_response()

        return CustomResponse(
            general_message='Groups assigned successfully'
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
