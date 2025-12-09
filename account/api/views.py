from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from .ses import AdministratorSerializer, UserLoginSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer, ChangePasswordSerializer, UserSerializer
from rest_framework import status, permissions
from rest_framework.views import APIView


class UserLoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        token, created = Token.objects.get_or_create(user=user)

        user_data = {
            "id": user.id,
            "full_name": user.full_name,
            "user_id": user.user_id,
            "role": user.role,
            "email": getattr(user, 'email', None),
        }

        response_data = {
            "token": token.key,
            "user": user_data
        }

        return Response(response_data, status=status.HTTP_200_OK)


class UserLogoutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, *args, **kwargs):
        Token.objects.filter(user=request.user).delete()
        return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)



class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        print("UserLoginView called")  # Debug log
        print("Incoming request data:", request.data)  # Debug log
        data = {
            "uidb64": request.data.get("uidb64"),
            "token": request.data.get("token"),
            "new_password1": request.data.get("new_password1"),
            "new_password2": request.data.get("new_password2"),
        }

        print("Payload passed to serializer:", data)  
        serializer = PasswordResetConfirmSerializer(data=data)
        if serializer.is_valid():
            try:
                result = serializer.save()
                print("Serializer save result:", result) 
                return Response(
                    result,  # Serializer returns {"detail": "Password has been reset successfully."}
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                print("Exception during save:", str(e))  
                return Response(
                    {"detail": f"An error occurred while resetting the password: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            print("Serializer errors:", serializer.errors)  # <--- this will tell us the reason
       
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data, context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response({'detail': "Password changed successfully"}, status=status.HTTP_200_OK)

        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )


class PasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            try:
                result = serializer.save(request)
                return Response(result, status=status.HTTP_200_OK)
            except Exception as e:
                return Response(
                    {"detail": "An error occurred while processing your request."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from account.api.ses import UserSerializerForCreateUser

User = get_user_model()

from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import get_user_model

User = get_user_model()

class AdministratorViewSet(ModelViewSet):
    serializer_class = AdministratorSerializer

    def get_queryset(self):
        return User.objects.filter(role="administrator")

    def perform_create(self, serializer):
        email = serializer.validated_data.get("email") or serializer.validated_data.get("user_id")
        serializer.save(
            role="administrator",
            user_id=email,  # use the email as user_id
            email=email,
            password="TempPassword123!"
        )



    def perform_update(self, serializer):
        # Prevent role change during update
        serializer.save(role="administrator")
