from django.views import View
from django.http import Http404
from django.contrib.auth.mixins import AccessMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied

class CustomLoginRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied 
        return super().dispatch(request, *args, **kwargs)
    
class UserRoleMixin(View):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  
        
        user = self.request.user
        context['is_guardian'] = user.groups.filter(name='Guardian').exists()
        context['is_assistant'] = user.groups.filter(name='Assistant').exists()
        context['is_therapist'] = user.groups.filter(name='Therapist').exists()
        context['is_administrator'] = user.groups.filter(name='Administrator').exists()

        return context

    def get_role_based_queryset(self, model_class):
        user = self.request.user
        
        if user.groups.filter(name__in=['Therapist', 'Assistant']).exists():
            return model_class.objects.all()
        
        elif user.groups.filter(name='Guardian').exists():
            return model_class.objects.filter(account_id=user)
        
        else:
            raise Http404("You do not have permission to view these records.")

class RolePermissionRequiredMixin(PermissionRequiredMixin):
    allowed_roles = []

    def has_permission(self):
        user = self.request.user

        # Ensure the user is authenticated
        if not user.is_authenticated:
            return False

        # Check if the user is part of any of the allowed groups
        if user.groups.filter(name__in=self.allowed_roles).exists():
            return True

        return False
    
    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission():
            raise PermissionDenied("You do not have permission to access this page.")
        return super().dispatch(request, *args, **kwargs)