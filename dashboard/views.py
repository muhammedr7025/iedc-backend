from rest_framework.views import APIView

from utils.response import CustomResponse


class RegisterAPI(APIView):
    def post(self, request):
        return CustomResponse(general_message='hi').get_success_response()
