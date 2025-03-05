from django.contrib import admin
from .models import (
    AdminRole, 
    HackathonRequest, 
    AdminLog, 
    UserBlock, 
    Analytics, 
    OrganizerDashboard
)

@admin.register(AdminRole)
class AdminRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'assigned_by', 'assigned_at')
    list_filter = ('role',)
    search_fields = ('user__name', 'assigned_by__name')
    date_hierarchy = 'assigned_at'

@admin.register(HackathonRequest)
class HackathonRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'expected_start_date', 'expected_end_date', 'reviewed_by')
    list_filter = ('status',)
    search_fields = ('title', 'user__name', 'reviewed_by__name')
    date_hierarchy = 'created_at'
    readonly_fields = ('reviewed_at',)

@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'entity_type', 'entity_id', 'created_at')
    list_filter = ('action', 'entity_type')
    search_fields = ('user__name', 'description')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)

@admin.register(UserBlock)
class UserBlockAdmin(admin.ModelAdmin):
    list_display = ('user', 'blocked_by', 'blocked_until', 'is_active', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__name', 'blocked_by__name', 'reason')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)

@admin.register(Analytics)
class AnalyticsAdmin(admin.ModelAdmin):
    list_display = ('date', 'new_users', 'active_users', 'hackathons_created', 'hackathons_completed', 'solutions_submitted')
    list_filter = ('date',)
    date_hierarchy = 'date'

@admin.register(OrganizerDashboard)
class OrganizerDashboardAdmin(admin.ModelAdmin):
    list_display = ('organizer', 'hackathon', 'participants_count', 'teams_count', 'solutions_count', 'average_score', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('organizer__name', 'hackathon__name')
    date_hierarchy = 'updated_at'
    readonly_fields = ('updated_at',)
