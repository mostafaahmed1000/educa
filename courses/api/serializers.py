from rest_framework import serializers
from courses.models import Subject, Course, Module, Content
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType  # Add this import
from courses.models import Text, File, Image, Video
from django.utils.text import slugify  # Add this import at the top

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['order', 'title', 'description']

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username

class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    owner = UserSerializer(read_only=True)
    slug = serializers.SlugField(read_only=True)  # Make slug read-only

    class Meta:
        model = Course
        fields = [
            "id",
            "subject",
            "title",
            "slug",
            "overview",
            "created",
            "owner",
            "modules",
            "image",
        ]

    def create(self, validated_data):
        # Generate slug from title
        title = validated_data['title']
        slug = slugify(title)
        
        # Handle duplicate slugs
        if Course.objects.filter(slug=slug).exists():
            count = 1
            while Course.objects.filter(slug=f"{slug}-{count}").exists():
                count += 1
            slug = f"{slug}-{count}"
            
        validated_data['slug'] = slug
        return super().create(validated_data)

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ["id", "title", "slug"]
        
class SubjectDetailSerializer(serializers.ModelSerializer):
    courses = CourseSerializer(many=True)
    class Meta:
        model = Subject
        fields = ["id", "title", "slug", "courses"]

class ItemRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return value.render()

class ContentSerializer(serializers.ModelSerializer):
    item = ItemRelatedField(read_only=True)
    class Meta:
        model = Content
        fields = [
            "id",
            "order",
            "item",
        ]
    
class ModuleWithContentsSerializer(serializers.ModelSerializer):
    contents = ContentSerializer(many=True)
    class Meta:
        model = Module
        fields = [
            "id",
            "order",
            "title",
            "description",
            "contents",
        ]
    
class CourseWithContentsSerializer(serializers.ModelSerializer):
    modules = ModuleWithContentsSerializer(many=True)
    owner = UserSerializer(read_only=True)  # Add this line

    class Meta:
        model = Course
        fields = [
            "id",
            "subject",
            "title",
            "slug",
            "overview",
            "created",
            "owner",
            "modules",
        ]

class ContentCreateSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField()
    title = serializers.CharField(write_only=True)
    text = serializers.CharField(required=False)
    file = serializers.FileField(required=False, allow_empty_file=False)
    image = serializers.ImageField(required=False, allow_empty_file=False)
    url = serializers.URLField(required=False)

    class Meta:
        model = Content
        fields = ['module', 'content_type', 'title', 'text', 'file', 'image', 'url', 'order']
        read_only_fields = ['item']

    def validate(self, attrs):
        content_type = attrs.get('content_type')
        # Validate required fields based on content_type
        if content_type == 'text' and not attrs.get('text'):
            raise serializers.ValidationError({'text': 'Text content is required for text type'})
        elif content_type == 'file' and not attrs.get('file'):
            raise serializers.ValidationError({'file': 'File is required for file type'})
        elif content_type == 'image' and not attrs.get('image'):
            raise serializers.ValidationError({'image': 'Image is required for image type'})
        elif content_type == 'video' and not attrs.get('url'):
            raise serializers.ValidationError({'url': 'URL is required for video type'})
        return attrs

    def to_representation(self, instance):
        # Override to include the item's title in the response
        representation = super().to_representation(instance)
        representation['title'] = instance.item.title
        return representation

    def validate_content_type(self, value):
        content_types = {
            'text': Text,
            'file': File,
            'image': Image,
            'video': Video
        }
        if value not in content_types:
            raise serializers.ValidationError('Invalid content type')
        return value

    def create(self, validated_data):
        content_type = validated_data.pop('content_type')
        title = validated_data.pop('title')
        content_types = {
            'text': Text,
            'file': File,
            'image': Image,
            'video': Video
        }
        
        item_data = {
            'title': title,
            'owner': self.context['request'].user
        }
        
        # Handle file uploads properly
        if content_type == 'text':
            item_data['content'] = validated_data.pop('text')
        elif content_type == 'file':
            file_obj = validated_data.pop('file')
            if file_obj:
                item_data['file'] = file_obj
        elif content_type == 'image':
            image_obj = validated_data.pop('image')
            if image_obj:
                item_data['file'] = image_obj
        elif content_type == 'video':
            item_data['url'] = validated_data.pop('url')

        # Create the specific content item
        ModelClass = content_types[content_type]
        item = ModelClass.objects.create(**item_data)

        # Create Content object with correct content type
        content = Content.objects.create(
            module=validated_data['module'],
            item=item,
            content_type=ContentType.objects.get_for_model(ModelClass),
            object_id=item.id,
            order=validated_data.get('order', 0)
        )

        return content

