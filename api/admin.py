from django.contrib import admin

from .models import *
# Register your models here.
admin.site.register(Equation)
admin.site.register(Description)
admin.site.register(EquationImageModel)
admin.site.register(CharacterImage)


