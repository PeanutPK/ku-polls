"""Setup for django admin page."""
from django.contrib import admin

from .models import Choice, Question


class ChoiceInline(admin.TabularInline):
    """Inline class for a Choice model which will be shown in Question."""

    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    """Question model for admin to configuration in the page."""

    fieldsets = [
        (None, {"fields": ["question_text"]}),
        (
            "Date information",
            {"fields": ["pub_date", "end_date"], "classes": ["collapse"]}),
    ]
    inlines = [ChoiceInline]
    list_display = ["question_text", "pub_date", "was_published_recently"]
    list_filter = ["pub_date"]
    search_fields = ["question_text"]


admin.site.register(Question, QuestionAdmin)
