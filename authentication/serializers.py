from rest_framework import serializers
from django.contrib.auth.models import User
from user_rol.models import Role, UserRole


class UserSerializer(serializers.ModelSerializer):
    # Cambia 'roles' a un campo de 'PrimaryKeyRelatedField' pero relacionado con la tabla intermedia 'UserRole'
    roles = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), many=True)
    
    class Meta:
        #Genera automáticamente los campos
        model = User 
        #Campos que el serializer tendrá en cuenta
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'password', 'roles']
        #Opción adicional, para que no se incluya en datos json
        extra_kwarg = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        #Extrae el campo roles
        roles = validated_data.pop('roles', [])  
        print(roles)

        #Verificar que el campo roles esté presente y no vacío
        if not roles:
            raise serializers.ValidationError({'roles': 'This field is requiered.'})

        #Validar que todos los roles existen antes de proceder
        roles_obj = []
        for rol_id in roles:
            try:
                role = Role.objects.get(name=rol_id)
                roles_obj.append(role)
            except Role.DoesNotExist:
                raise serializers.ValidationError({'roles': f'El rol con id {rol_id} no existe.'})

        #Crear el usuario
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        
        if password:
            instance.set_password(password)
        instance.save()

        #Asignar roles al usuario
        for role in roles_obj:
            UserRole.objects.create(userid=instance, rolid=role)

        return instance
    
