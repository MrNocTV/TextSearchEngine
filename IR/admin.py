from django.contrib import admin
from .models import Doc, Term, Entry

# Register your models here.

class TermAdmin(admin.ModelAdmin):
    list_display = ("id", "content", "how_many", "idf")


admin.site.register(Doc)
admin.site.register(Term, TermAdmin)
admin.site.register(Entry)