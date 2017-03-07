from django.contrib import admin
from .models import Doc, Term, Entry

# Register your models here.
admin.site.register(Doc)
admin.site.register(Term)
admin.site.register(Entry)