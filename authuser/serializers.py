from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'name', 'mobile', 'location')

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data.get('name', ''),
            mobile=validated_data.get('mobile', ''),
            location=validated_data.get('location', '')
        )
        return user
