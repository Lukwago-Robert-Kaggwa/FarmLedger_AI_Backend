from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login

from authuser.models import User
from .serializers import UserSignUpSerializer

class UserSignUpView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserSignUpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            return JsonResponse({
                'message': 'Login successful',
                'user_id': user.id,  # Return the user's ID
                'email': user.email,
                'province': user.location,
                'name': user.name,
            })
        return Response({"error": "Invalid email or password"}, status=status.HTTP_400_BAD_REQUEST)
    
class UpdateUserView(APIView):
    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        email = request.data.get('email')
        name = request.data.get('name')
        location = request.data.get('province')

        User.objects.filter(id=user_id).update(name=name, email=email, location=location)

        user = get_object_or_404(User, id=user_id)
        
        if user is not None:
            return JsonResponse({
                'user_id': user.id,
                'email': user.email,
                'province': user.location,
                'name': user.name,
            })
        return Response({"error": "Invalid email or password"}, status=status.HTTP_400_BAD_REQUEST)