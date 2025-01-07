from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

User = get_user_model() 

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