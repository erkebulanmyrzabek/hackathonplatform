from django.contrib import admin
from .models import Hackathon, PrizePlaces

class PrizePlacesInline(admin.TabularInline):
    model = PrizePlaces
    extra = 1

@admin.register(Hackathon)
class HackathonAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'start_registation', 'end_hackathon', 'prize_pool', 'number_of_winners')
    list_filter = ('status', 'start_registation', 'end_hackathon')
    search_fields = ('name', 'description', 'tags')
    filter_horizontal = ('participants',)
    inlines = [PrizePlacesInline]
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'image', 'tags', 'status')
        }),
        ('Даты', {
            'fields': ('anonce_start', 'start_registation', 'end_registration', 'start_hackathon', 'end_hackathon')
        }),
        ('Призы и участники', {
            'fields': ('prize_pool', 'number_of_winners', 'participants')
        }),
    )

@admin.register(PrizePlaces)
class PrizePlacesAdmin(admin.ModelAdmin):
    list_display = ('hackathon', 'place', 'prize_amount', 'winner')
    list_filter = ('hackathon', 'place')
    search_fields = ('hackathon__name', 'winner__username')