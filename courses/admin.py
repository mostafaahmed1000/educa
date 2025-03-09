from django.contrib import admin
from .models import Content, Subject, Course, Module


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ["title", "slug"]
    prepopulated_fields = {"slug": ("title",)}


class ModuleInline(admin.StackedInline):
    model = Module


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "subject", "created"]
    list_filter = ["created", "subject"]
    search_fields = ["title", "overview"]
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ModuleInline]

@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ["id", "content_type", "item", "order", "module"]

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ["id","title", "course", "order"]