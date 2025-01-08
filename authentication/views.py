from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from authentication.utils import ExpiringPasswordResetTokenGenerator
from .serializers import UserSerializer
from django.core.mail import send_mail
from django.core.mail import BadHeaderError
from decouple import config
from smtplib import SMTPException
import logging
from rest_framework_simplejwt.views import ( TokenObtainPairView, TokenRefreshView,)
from django.contrib.auth.hashers import make_password

# Configura el logger si no lo tienes configurado
logger = logging.getLogger(__name__)

User = get_user_model() 

class Register (APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "User created sucessfully!"}, status=status.HTTP_201_CREATED)

class Login (TokenObtainPairView):
    def post(self, request,  *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found!')
        
        user_rol = user.roles.all()
        roles = [role.rolid.name for role in user_rol] 

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')
        
        if not user.is_active:
            Response({'error': 'El usuario no está activo'}, status=status.HTTP_403_FORBIDDEN)
        
        # Crear los tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Actualizar campos
        user.last_login = now()
        user.save()

        response = {
            'access_token': access_token,
            'refress_token': refresh_token,
            'id': user.id,
            'username': user.username,
            'name': user.first_name,
            'lastname': user.last_name,
            'email': user.email,
            'rol': roles,
            'message': 'Successfully Login!'
        }

        return Response(response, status=status.HTTP_200_OK)
    
class GenerateNewToken(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh')  

        if not refresh_token:
            return Response({'error': 'El refresh token es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Se pasa el refresh_token al TokenRefreshView para que lo maneje internamente
            original_response = super().post(request, *args, **kwargs)

            # Personalizar la respuesta 
            data = original_response.data
            data['message'] = 'Token refreshed successfully!'
            return Response(data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def Logout(request):
    # Buscar al usuario con el id proporcionado
    user = User.objects.filter(id=request.data.get('id', 0)).first()

    # Verificar si el usuario existe
    if user:
        # Invalidar todos los tokens para este usuario
        RefreshToken.for_user(user)
        print(str(RefreshToken))
        return Response({'message': 'Logout Successfully!'}, status=status.HTTP_200_OK)
    
    # Si no se encuentra el usuario
    return Response({'error': 'No existe este usuario.'}, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetRequest(APIView):
    def post(self, request):
        email = request.data.get('email')
        username = request.data.get('username')
        try:
            user = User.objects.get(email=email, username=username)
            token_generator = ExpiringPasswordResetTokenGenerator()
            token = token_generator.create_token(user, user.id)
            url_front = config('FRONTEND_URL')
            
            reset_link = f"{url_front}/auth/password_reset_validate/{token}"
            send_mail(
                f'Restablecimiento de contraseña por parte del usuario {user.username}',
                f'Recibimos una solicitud de tu parte. Usa este enlace para restablecer tu contraseña: {reset_link}',
                "test@test.com",
                [email],
                fail_silently=False
            )
            return Response({'message': 'Email successfully sent!'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_400_BAD_REQUEST)
        except BadHeaderError:
            logger.error("Error: Invalid header in the email.")
            return Response({'error': 'Bad header in the email request.'}, status=status.HTTP_400_BAD_REQUEST)
        except SMTPException as e:
            logger.error(f"SMTP error when sending the email: {e}")
            return Response({'error': f"SMTP error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Unnexpected error when sending the email: {e}")
            return Response({'error': 'Unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PasswordResetTokenValidation(APIView):
    def get(self, request, token):
        try:
            token_generator = ExpiringPasswordResetTokenGenerator()
            user_id, decoded_token, expiration = token_generator.decode_token(token)  # Decodifica y separa el token
            user = User.objects.get(id=user_id)
            
            if token_generator.is_token_valid(user, decoded_token, expiration):
                # Lógica de validación adicional, si es necesario
                return Response({'message': 'Token is valid', 'token':{token}}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Token has expired'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({'error': 'Invalid token format'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_400_BAD_REQUEST)
               
class PasswordResetTokenCompleted(APIView):
    def post(self, request):
        try:
            token = request.data.get('token') 
            token_generator = ExpiringPasswordResetTokenGenerator()
            user_id, decoded_token, expiration = token_generator.decode_token(token)
            user = User.objects.get(id=user_id)

            if token_generator.is_token_valid(user, decoded_token, expiration):
                new_password = request.data.get('new_password') 
                user.password = make_password(new_password)
                user.save()
                return Response({"message": "Reset password process completed."}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Token has expired'}, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_400_BAD_REQUEST)   
        except ValueError:
            return Response({'error': 'Invalid token format.'}, status=status.HTTP_400_BAD_REQUEST)