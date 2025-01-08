from django.contrib.auth.tokens import PasswordResetTokenGenerator
from datetime import timedelta
from django.utils.timezone import now, datetime, localtime
from django.contrib.auth.models import User
import base64

class ExpiringPasswordResetTokenGenerator(PasswordResetTokenGenerator):
    def create_token(self, user, id):
        """
        Crea un token que incluye la expiración.
        """
        token = super().make_token(user)
        expiration_time = localtime(now()) + timedelta(minutes=20)  # Token válido por 20 minutos
        #expiration_time se pasa a este formato YYYY-MM-DDTHH:MM:SS.mmmmmm y luego todo a byte
        combined = f"{id}|{token}|{expiration_time.isoformat()}".encode('utf-8')  # Combina y convierte a bytes
        #Codificar el combined
        return base64.urlsafe_b64encode(combined).decode('utf-8')  # Devuelve como cadena codificada
        
        
    def is_token_valid(self, user, token, expiration):
        """
        Verifica si el token es válido y no ha expirado.
        """
        try:
            # Validar la expiración
            expiration_time = datetime.fromisoformat(expiration)
            if now() > expiration_time:  # Token expirado
                return False

            # Validar el token usando Django's PasswordResetTokenGenerator
            token_generator = PasswordResetTokenGenerator()
            if not token_generator.check_token(user, token):
                return False

            # Si ambas validaciones pasan, el token es válido y no ha expirado
            return True
        except (ValueError, User.DoesNotExist):
            # Token no válido o usuario no encontrado
            return False

   
    def decode_token(self, encoded_token):
        """
        Decodifica un token generado por `create_token` y devuelve sus componentes.
        """
        try:
            # Decodifica desde base64
            decoded_bytes = base64.urlsafe_b64decode(encoded_token.encode('utf-8'))
            decoded_str = decoded_bytes.decode('utf-8')
            # Divide el token en sus componentes: el token original y la expiración
            id_str, token, expiration_str = decoded_str.rsplit('|', 2)
            return id_str, token, expiration_str
        except (ValueError, base64.binascii.Error) as e:
            raise ValueError("Token inválido o mal formado") from e

