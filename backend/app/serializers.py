from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.password_validation import validate_password

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirmPassword = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'confirmPassword', 'pharmacyName', 'registrationNumber', 'address', 'registrationCertificate','terms']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirmPassword']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email'],
            pharmacyName=validated_data['pharmacyName'],
            registrationNumber=validated_data['registrationNumber'],
            address=validated_data['address'],
            registrationCertificate=validated_data.get('registrationCertificate'),
            terms=validated_data['terms'],
        )
        user.set_password(validated_data['password'])  # Hash the password
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # Ensure that the user exists
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")

        # Verify password
        if not user.check_password(password):
            raise serializers.ValidationError("Incorrect password.")

        attrs['user'] = user
        return attrs
