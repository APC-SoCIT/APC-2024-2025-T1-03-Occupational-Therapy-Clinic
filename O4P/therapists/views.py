from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.models import TherapistInformation as Therapist
from .models import AvailableSlot, DAYS_OF_WEEK
from .forms import TherapistScheduleForm
from datetime import datetime
from collections import defaultdict, OrderedDict

# Check if the user is in the Therapist group
def is_therapist(user):
    return user.groups.filter(name="Therapist").exists()


@login_required
@user_passes_test(is_therapist)
def list_schedule(request):
    therapist = Therapist.objects.get(account_id=request.user)

    slots = therapist.available_slots.all().order_by('day', 'start_time')
    
    # Sort days according to defined order
    day_order = {day[0]: index for index, day in enumerate(DAYS_OF_WEEK)}
    
    # Group slots by day and determine the first and last slot
    schedule_summary = OrderedDict()
    for slot in slots:
        if slot.day not in schedule_summary:
            schedule_summary[slot.day] = {'start_time': slot.start_time, 'end_time': slot.end_time, 'slot_id': slot.id}
        else:
            schedule_summary[slot.day]['start_time'] = min(schedule_summary[slot.day]['start_time'], slot.start_time)
            schedule_summary[slot.day]['end_time'] = max(schedule_summary[slot.day]['end_time'], slot.end_time)
    
    # Sort the dictionary by day order
    sorted_schedule = OrderedDict(sorted(schedule_summary.items(), key=lambda x: day_order[x[0]]))
    
    return render(request, 'therapists/schedule_list.html', {'schedule_summary': sorted_schedule})



@login_required
@user_passes_test(is_therapist)
def create_schedule(request):
    therapist = Therapist.objects.get(account_id=request.user)
    if request.method == 'POST':
        form = TherapistScheduleForm(request.POST)
        if form.is_valid():
            selected_days = form.cleaned_data['available_days']
            selected_slots = form.cleaned_data['available_slots']
            
            for day in selected_days:
                for slot in selected_slots:
                    start_str, end_str = slot.split('-')
                    start_time = datetime.strptime(start_str, '%H:%M').time()
                    end_time = datetime.strptime(end_str, '%H:%M').time()
                    AvailableSlot.objects.create(
                        therapist=therapist,
                        day=day,
                        start_time=start_time,
                        end_time=end_time
                    )
            return redirect('list_schedule')
    else:
        form = TherapistScheduleForm()
    return render(request, 'therapists/schedule_form.html', {'form': form})

@login_required
@user_passes_test(is_therapist)
def update_schedule(request, slot_id):
        # ✅ Get the therapist instance instead of using request.user directly
    therapist = Therapist.objects.get(account_id=request.user)

    # ✅ Now use the therapist instance in the query
    slot = get_object_or_404(AvailableSlot, id=slot_id, therapist=therapist)
    if request.method == 'POST':
        form = TherapistScheduleForm(request.POST)
        if form.is_valid():
            slot.day = form.cleaned_data['available_days'][0]
            slot.start_time, slot.end_time = [
                datetime.strptime(t, '%H:%M').time() for t in form.cleaned_data['available_slots'][0].split('-')
            ]
            slot.save()
            return redirect('list_schedule')
    else:
        form = TherapistScheduleForm(initial={
            'available_days': [slot.day],
            'available_slots': [f"{slot.start_time.strftime('%H:%M')}-{slot.end_time.strftime('%H:%M')}"]
        })
    return render(request, 'therapists/schedule_form.html', {'form': form})

@login_required
@user_passes_test(is_therapist)
def delete_schedule(request, slot_id):
        # ✅ Get the therapist instance instead of using request.user directly
    therapist = Therapist.objects.get(account_id=request.user)

    # ✅ Now use the therapist instance in the query
    slot = get_object_or_404(AvailableSlot, id=slot_id, therapist=therapist)
    if request.method == 'POST':
        slot.delete()
        return redirect('list_schedule')
    return render(request, 'therapists/schedule_confirm_delete.html', {'slot': slot})