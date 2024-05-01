from django.contrib import admin
from .models import MainMenu,BodyPart,Sport,SportHistory

# Register your models here.
@admin.register(MainMenu)
class MainMenuAdmin(admin.ModelAdmin):
    list_display = ['id',"title"]
    # prepopulated_fields = {"slug": ("title",)}

@admin.register(BodyPart)
class BodyPartAdmin(admin.ModelAdmin):
    list_display = ["name"]

@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    list_display=['name','slug','createdBy']
    prepopulated_fields={'slug':('name',)}

@admin.register(SportHistory)
class SportHistoryAdmin(admin.ModelAdmin):
    list_display=['id','user_id','sport_id','set_number','count','weight','sport_date']