from rest_framework.views import APIView
from utils.response import CustomResponse

from dashboard.serializer import UserRegisterSerializer

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
