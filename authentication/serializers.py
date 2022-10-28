from rest_framework.serializers import ModelSerializer, EmailField, \
    CharField, ValidationError

from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

from .models import User


class RegisterSerializer(ModelSerializer):
    email = EmailField(required=True,
                       validators=
                       [UniqueValidator(queryset=User.objects.all())])

    password = CharField(write_only=True,
                         required=True,
                         validators=[validate_password])
    password2 = CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise ValidationError(
                {"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
