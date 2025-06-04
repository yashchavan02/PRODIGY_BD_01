import uuid
from datetime import datetime
from rest_framework import status
from rest_framework.views import APIView
from app.serializers import UserSerializer
from rest_framework.response import Response

USER_STORAGE = {}

def get_users():
    return list(USER_STORAGE.values())

def get_user(user_id):
    return USER_STORAGE.get(str(user_id))

def save_user(user_data):
    if 'id' not in user_data:
        user_data['id'] = str(uuid.uuid4())
    USER_STORAGE[user_data['id']] = user_data
    return user_data

def delete_user(user_id):
    if str(user_id) in USER_STORAGE:
        del USER_STORAGE[str(user_id)]
        return True
    return False



class UserListCreateView(APIView):

    def get(self, request):
        users = get_users()
        return Response({
            'status': 'success',
            'data': users,
            'count': len(users)
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            for user in get_users():
                if user.get('email', '').lower() == serializer.validated_data['email'].lower():
                    return Response({
                        'status': 'error',
                        'message': 'User with this email already exists.',
                        'errors': {'email': ['This email is already registered.']}
                    }, status=status.HTTP_400_BAD_REQUEST)
            user_data = serializer.validated_data.copy()
            user_data['id'] = str(uuid.uuid4())
            user_data['created_at'] = datetime.now().isoformat()
            user_data['updated_at'] = datetime.now().isoformat()
            saved_user = save_user(user_data)
            return Response({
                'status': 'success',
                'message': 'User created successfully.',
                'data': saved_user
            }, status=status.HTTP_201_CREATED)

        return Response({
            'status': 'error',
            'message': 'Validation failed.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):

    def get(self, request, user_id):
        user_data = get_user(user_id)
        if not user_data:
            return Response({'status': 'error', 'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'status': 'success', 'data': user_data}, status=status.HTTP_200_OK)

    def put(self, request, user_id):
        user_data = get_user(user_id)
        if not user_data:
            return Response({'status': 'error', 'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            for user in get_users():
                if user.get('email', '').lower() == serializer.validated_data['email'].lower() and user.get('id') != str(user_id):
                    return Response({
                        'status': 'error',
                        'message': 'User with this email already exists.',
                        'errors': {'email': ['This email is already registered.']}
                    }, status=status.HTTP_400_BAD_REQUEST)

            updated_data = user_data.copy()
            updated_data.update(serializer.validated_data)
            updated_data['updated_at'] = datetime.now().isoformat()
            saved_user = save_user(updated_data)
            return Response({
                'status': 'success',
                'message': 'User updated successfully.',
                'data': saved_user
            }, status=status.HTTP_200_OK)

        return Response({
            'status': 'error',
            'message': 'Validation failed.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        if delete_user(user_id):
            return Response({
                'status': 'success',
                'message': 'User deleted successfully.'
            }, status=status.HTTP_200_OK)
        return Response({
            'status': 'error',
            'message': 'User not found.'
        }, status=status.HTTP_404_NOT_FOUND)
