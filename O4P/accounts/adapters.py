from allauth.account.adapter import DefaultAccountAdapter

class CustomAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return True  # Allow all users to sign up

    def confirm_email(self, request, email_address):
        """
        Override email confirmation to prevent auto-activation for staff accounts.
        Guardians are activated immediately, while Therapists and Assistants remain inactive.
        """
        email_address.verified = True
        email_address.save()

        user = email_address.user
        
        if user.groups.filter(name="Assistant").exists():  
            user.is_active = False  # Auto-activate Guardians
        elif user.groups.filter(name="Therapist").exists():
            user.is_active = False
        else:
            user.is_active = True  # Keep staff accounts inactive

        user.save()
