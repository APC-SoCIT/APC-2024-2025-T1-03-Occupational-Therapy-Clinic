from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.generic.edit import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import PatientInformation
from .models import PatientNotes
from .forms import PatientInformationForm
from .forms import PatientNotesForm
from core.mixins import UserRoleMixin
from core.mixins import RolePermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.shortcuts import redirect
from django.http import JsonResponse
from django.urls import reverse_lazy
from allauth.account.views import SignupView
from django.http import HttpResponseForbidden
from games.models import AssignedGame, Game
from django.views import View
from django.contrib import messages

#
# PATIENTS
#
class PatientInformationCreateView(RolePermissionRequiredMixin, CreateView):
    model = PatientInformation
    form_class = PatientInformationForm
    template_name = "patients/patients_information_form.html"
    allowed_roles = ['Guardian']
    success_url = reverse_lazy('patients.list')

    def form_valid(self, form):
        guardian = self.request.user  # The logged-in guardian
        
        # Count existing patients for this guardian
        patient_count = PatientInformation.objects.filter(account_id=guardian).count()

        if patient_count >= 10:  # Set your patient limit
            messages.error(self.request, "A guardian can have a maximum of 10 patients. Current patient count: " + str(patient_count))
            return redirect(self.request.path)  # Reload the form with an error message

        # Assign the guardian before saving
        form.instance.account_id = guardian
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    
class PatientsListView(LoginRequiredMixin, UserRoleMixin, ListView):
    model = PatientInformation
    context_object_name = "patients"
    template_name = "patients/patients_list.html"

    def get_queryset(self):
        queryset = self.get_role_based_queryset(PatientInformation)
        search_query = self.request.GET.get('q', '')

        if search_query:
            queryset = queryset.filter(
                first_name__icontains=search_query
            ) | queryset.filter(
                last_name__icontains=search_query
            ) | queryset.filter(
                diagnosis__icontains=search_query
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context

class PatientDetailView(LoginRequiredMixin, UserRoleMixin, DetailView,):
    model = PatientInformation
    template_name = 'patients/patients_detail.html'
    context_object_name = "patient"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.get_object()
        user = self.request.user

        context['patient_notes'] = PatientNotes.objects.filter(patient_id=patient)

        # Retrieve assigned games
        context['assigned_games'] = AssignedGame.objects.filter(patient=patient)
        context['available_games'] = []

        # Retrieve available games for therapists to assign
        if user.groups.filter(name='Therapist').exists():
            assigned_game_ids = AssignedGame.objects.filter(patient=patient).values_list('game_id', flat=True)
            context['available_games'] = Game.objects.exclude(id__in=assigned_game_ids)  # Exclude assigned games
        
        context['is_patient'] = user.groups.filter(name='Patient').exists()
        context['is_guardian'] = user.groups.filter(name='Guardian').exists()
        context['is_assistant'] = user.groups.filter(name='Assistant').exists()
        context['is_therapist'] = user.groups.filter(name='Therapist').exists()
        context['is_administrator'] = user.groups.filter(name='Administrator').exists()

        return context
    
    def get_queryset(self):
        return self.get_role_based_queryset(PatientInformation)
    
class PatientsUpdateView(LoginRequiredMixin, UserRoleMixin, UpdateView):
    model = PatientInformation
    form_class = PatientInformationForm
    template_name = "patients/patients_form.html"
   
    def test_func(self):
        return self.request.user.groups.filter(name__in=['Therapist']).exists()
    
    def get_queryset(self):
        user = self.request.user
        
        if user.groups.filter(name__in=['Guardian', 'Assistant']).exists():
            raise PermissionDenied
       
        return super().get_queryset()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = self.object  
        return context
    
    def get_success_url(self):
        return reverse_lazy('patients.details', kwargs={'pk': self.object.pk})

class PatientsDeleteView(LoginRequiredMixin, UserRoleMixin, DeleteView):
    model = PatientInformation
    template_name = "patients/patients_delete.html"
    success_url = reverse_lazy('patients.list')
    
    def test_func(self):
        return self.request.user.groups.filter(name__in=['Therapist']).exists()
    
    def get_queryset(self):
        user = self.request.user
        
        if user.groups.filter(name__in=['Guardian', 'Assistant']).exists():
            raise PermissionDenied
        
        return super().get_queryset()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = get_object_or_404(PatientInformation, pk=self.object.pk)  
        return context

"""
PATIENT NOTES
"""

class NoteDetailView(LoginRequiredMixin, DetailView):
    model = PatientNotes
    template_name = 'patients_notes/note_details.html'
    context_object_name = "note"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        note = self.get_object()

        context['patient_notes'] = PatientNotes.objects.filter(patient=note.patient)

        user = self.request.user
        context['is_guardian'] = user.groups.filter(name='Guardian').exists()
        context['is_assistant'] = user.groups.filter(name='Assistant').exists()
        context['is_therapist'] = user.groups.filter(name='Therapist').exists()
        context['is_administrator'] = user.groups.filter(name='Administrator').exists()

        patient = note.patient
        context['patient'] = patient
        return context
    
    def get_queryset(self):
        user = self.request.user
        note_id = self.kwargs.get('pk')  

        try:
            note = PatientNotes.objects.get(id=note_id)  
            patient = note.patient    
        except PatientNotes.DoesNotExist:
            return PatientNotes.objects.none()  

        if user.groups.filter(name='Guardian').exists():
            patients = PatientInformation.objects.filter(account_id=user)

            if patient in patients:  
                return PatientNotes.objects.filter(patient=patient)
            else:
                return PatientNotes.objects.none()

        elif user.groups.filter(name__in=['Therapist', 'Assistant']).exists():
            return PatientNotes.objects.all()

        else:
            raise PermissionDenied


        
class NoteCreateView(RolePermissionRequiredMixin, CreateView):
    model = PatientNotes
    form_class = PatientNotesForm
    template_name = "patients_notes/note_form.html"
    allowed_roles = ['Therapist']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = get_object_or_404(PatientInformation, id=self.kwargs['pk'])
        context['patient'] = patient 
        return context

    def form_valid(self, form):
        patient = get_object_or_404(PatientInformation, id=self.kwargs['pk'])
        form.instance.patient = patient
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('patients.details', kwargs={'pk': self.kwargs['pk']})

class NotesUpdateView(RolePermissionRequiredMixin, UpdateView):
    model = PatientNotes
    form_class = PatientNotesForm
    template_name = "patients_notes/note_form.html"
    allowed_roles = ['Therapist']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        note = self.get_object()

        context['patient_notes'] = PatientNotes.objects.filter(patient=note.patient)

        user = self.request.user
        context['is_guardian'] = user.groups.filter(name='Guardian').exists()
        context['is_assistant'] = user.groups.filter(name='Assistant').exists()
        context['is_therapist'] = user.groups.filter(name='Therapist').exists()
        context['is_administrator'] = user.groups.filter(name='Administrator').exists()

        patient = note.patient
        context['patient'] = patient
        return context

    def get_success_url(self):
        return reverse('patients.details', kwargs={'pk': self.object.patient.pk})
    
class NotesDeleteView(RolePermissionRequiredMixin, DeleteView):
    model = PatientNotes 
    template_name='patients_notes/note_delete.html'
    allowed_roles = ['Therapist']
    
    def get_success_url(self):
        return reverse('patients.details', kwargs={'pk': self.object.patient.pk})

class AssignGameView(LoginRequiredMixin, View):
    def post(self, request, patient_id):
        if not request.user.groups.filter(name='Therapist').exists():
            return HttpResponseForbidden("Only therapists can assign games.")
        
        patient = get_object_or_404(PatientInformation, id=patient_id)
        game = get_object_or_404(Game, id=request.POST.get('game_id'))
        
        AssignedGame.objects.create(patient=patient, game=game)
        return redirect('patients.details', pk=patient.id)

class RemoveAssignedGameView(LoginRequiredMixin, View):
    def post(self, request, patient_id, assigned_game_id):
        if not request.user.groups.filter(name='Therapist').exists():
            return HttpResponseForbidden("Only therapists can remove assigned games.")
        
        assigned_game = get_object_or_404(AssignedGame, id=assigned_game_id, patient_id=patient_id)
        assigned_game.delete()
        return redirect('patients.details', pk=patient_id)