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

    def get_role_based_queryset(self, queryset, model_class):
        """
        Returns a queryset based on the user's role.
        - Therapists get all records.
        - Patients get only their own records.
        - Others (like Assistants or Guardians) get nothing or customized sets.
        """
        user = self.request.user
        
        if user.groups.filter(name='Therapist').exists():
            return model_class.objects.all()
        elif user.groups.filter(name='Patient').exists():
            return model_class.objects.filter(account_id=user)
        else:
            raise Http404("You do not have permission to view these records.")
