from django.views import View
from django.http import Http404

class UserRoleMixin(View):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  
        
        user = self.request.user
        context['is_patient'] = user.groups.filter(name='Patient').exists()
        context['is_guardian'] = user.groups.filter(name='Guardian').exists()
        context['is_assistant'] = user.groups.filter(name='Assistant').exists()
        context['is_therapist'] = user.groups.filter(name='Therapist').exists()

        return context

    def get_role_based_queryset(self, model_class):
        """
        Returns a queryset based on the user's role.
        - Therapists and Assistants get all records.
        - Patients get only their own records.
        - Guardians get all records whose guardian id matches them.
        """
        user = self.request.user
        
        if user.groups.filter(name__in=['Therapist', 'Assistant']).exists():
            # Therapists and Assistants get all patient records
            return model_class.objects.all()
        
        elif user.groups.filter(name='Patient').exists():
            # Patients get only their own records
            return model_class.objects.filter(account_id=user)
        
        #elif user.groups.filter(name='Guardian').exists():
            # Guardians get all records whose guardian_id matches their user id
        #    return model_class.objects.filter(guardian_id=user.id)
        
        else:
            raise Http404("You do not have permission to view these records.")
