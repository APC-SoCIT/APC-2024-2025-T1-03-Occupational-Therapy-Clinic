from django.views import View
from django.http import Http404
from patients.models import Guardian

class UserRoleMixin(View):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  
        
        user = self.request.user
        context['is_patient'] = user.groups.filter(name='Patient').exists()
        context['is_guardian'] = user.groups.filter(name='Guardian').exists()
        context['is_assistant'] = user.groups.filter(name='Assistant').exists()
        context['is_therapist'] = user.groups.filter(name='Therapist').exists()
        context['is_administrator'] = user.groups.filter(name='Administrator').exists()

        return context

    def get_role_based_queryset(self, model_class):
        """
        Returns a queryset based on the user's role.
        - Therapists and Assistants get all records.
        - Patients get only their own records.
        - Guardians get all records whose guardian id matches them.
        """
        user = self.request.user
        
        if user.groups.filter(name__in=['Therapist', 'Assistant', 'Administrator']).exists():
            return model_class.objects.all()
        
        elif user.groups.filter(name='Patient').exists():
            return model_class.objects.filter(account_id=user)
        
        elif user.groups.filter(name='Guardian').exists():
            try:
                guardian = Guardian.objects.get(user=user)
                return model_class.objects.filter(guardian=guardian)  
            except Guardian.DoesNotExist:
                return model_class.objects.none()  
        
        else:
            raise Http404("You do not have permission to view these records.")
