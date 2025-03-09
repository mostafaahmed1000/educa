from rest_framework import generics, viewsets, status
from courses.models import Subject, Course, Content, Module
from courses.api.serializers import SubjectSerializer, CourseSerializer, CourseWithContentsSerializer, SubjectDetailSerializer, ContentCreateSerializer
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from courses.api.permissions import IsEnrolled, IsOwner
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes

class SubjectListView(generics.ListAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class SubjectDetailView(generics.RetrieveAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectDetailSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [AllowAny]  # Default to allow anyone to view courses

    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy',  'add_module', 'add_content', 'remove_content', 'get_owned_courses']:
            permission_classes = [IsAuthenticated, IsOwner]
        elif self.action in ['enroll', 'contents', 'enrolled']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]  # For list and retrieve actions
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    # Override default methods to ensure proper permission checks
    def update(self, request, *args, **kwargs):
        course = self.get_object()
        if course.owner != request.user:
            return Response({'error': 'Not authorized'}, 
                          status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        course = self.get_object()
        if course.owner != request.user:
            return Response({'error': 'Not authorized'}, 
                          status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    # Existing actions for enrollment and content viewing
    @action(detail=True,
            methods=['post'],
            permission_classes=[IsAuthenticated])
    def enroll(self, request, *args, **kwargs):
        course = self.get_object()
        course.students.add(request.user)
        return Response({'enrolled': True})

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def enrolled(self, request):
        courses = Course.objects.filter(students=request.user)
        serializer = self.get_serializer(courses, many=True)
        return Response(serializer.data)

    # New actions for content management
    @action(detail=True,
            methods=['post'],
            permission_classes=[IsAuthenticated, IsOwner],
            url_path='add-module')
    def add_module(self, request, *args, **kwargs):
        course = self.get_object()
        title = request.data.get('title')
        description = request.data.get('description')
        
        if not title:
            return Response({'error': 'Title is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        module = Module.objects.create(course=course, title=title, description=description)
        return Response({
            'id': module.id,
            'title': module.title,
            'description': module.description
        }, status=status.HTTP_201_CREATED)

    @action(detail=True,
            methods=['delete'],
            permission_classes=[IsAuthenticated, IsOwner],
            url_path='remove-module/(?P<module_id>[^/.]+)')
    def remove_module(self, request, module_id, *args, **kwargs):
        course = self.get_object()
        try:
            module = Module.objects.get(id=module_id, course=course)
            module.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Module.DoesNotExist:
            return Response({'error': 'Module not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
            
   
    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated],
            url_path='owned-courses')
    def get_owned_courses(self, request):
        """Get all courses owned by the current user"""
        courses = Course.objects.filter(owner=request.user)
        serializer = self.get_serializer(courses, many=True)
        return Response({
            'owned_courses': serializer.data,
            'total_courses': courses.count()
        }, status=status.HTTP_200_OK)

    @action(detail=True,
            methods=['get'],
            permission_classes=[IsAuthenticated, IsEnrolled],
            serializer_class=CourseWithContentsSerializer)
    def contents(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class ContentCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = ContentCreateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        return context  # This already includes the request

    def perform_create(self, serializer):
        module_id = self.kwargs['module_id']
        module = get_object_or_404(Module, id=module_id)
        
        # Check if user is the owner of the course
        if module.course.owner != self.request.user:
            raise PermissionDenied("You are not allowed to add content to this module")
            
        serializer.save(module=module)



class ContentDetailView(generics.RetrieveDestroyAPIView):
    queryset = Content.objects.all()
    serializer_class = ContentCreateSerializer
    permission_classes = [IsAuthenticated]

    def check_object_permissions(self, request, obj):
        if (obj.module.course.owner != request.user):
            raise PermissionDenied("You are not allowed to modify this content")
        return super().check_object_permissions(request, obj)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.item.delete()  # Delete the associated item first
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([AllowAny])
def user_login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {"error": "Please provide both username and password"}, status=400
        )

    user = authenticate(username=username, password=password)

    if not user:
        return Response({"error": "Invalid credentials"}, status=401)

    token, _ = Token.objects.get_or_create(user=user)

    return Response(
        {
            "token_type": "Token",
            "token": token.key,
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
        }
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def user_signup(request):
    username = request.data.get("username")
    password = request.data.get("password")
    email = request.data.get("email", "")

    if not username or not password:
        return Response(
            {"error": "Please provide both username and password"}, status=400
        )

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists"}, status=400)

    user = User.objects.create_user(username=username, password=password, email=email)

    token, _ = Token.objects.get_or_create(user=user)

    return Response(
        {
            "token_type": "Token",
            "token": token.key,
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
        },
        status=201,
    )
