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
        print("🔹 POST DATA:", request.POST)  # Debugging: See what is being sent

        form = TherapistScheduleForm(request.POST)

        if form.is_valid():
            selected_days = request.POST.getlist('available_days')
            print("✅ Selected Days:", selected_days)  # Debugging: See selected days

            selected_slots = []
            for day in selected_days:
                slot_data_list = request.POST.getlist(f'selected_slots_{day}')  # Retrieve slot data

                # Flatten slot list and remove empty values
                slot_list = []
                for slot_data in slot_data_list:
                    slot_list.extend([slot.strip() for slot in slot_data.split(',') if slot.strip()])

                print(f"🕒 Slots for {day}: {slot_list}")  # Debugging: Check received slots

                for slot in slot_list:
                    if '-' in slot:
                        selected_slots.append((day, slot))

            print("✅ Processed Slots:", selected_slots)  # Debugging: Check processed slots

            # Save slots into the database
            for day, slot in selected_slots:
                try:
                    start_str, end_str = slot.split('-')
                    start_time = datetime.strptime(start_str, '%H:%M').time()
                    end_time = datetime.strptime(end_str, '%H:%M').time()

                    print(f"📝 Saving Slot: {day} {start_time}-{end_time}")  # Debugging: See what is being saved

                    # Avoid duplicate slot entries
                    if not AvailableSlot.objects.filter(therapist=therapist, day=day, start_time=start_time, end_time=end_time).exists():
                        AvailableSlot.objects.create(
                            therapist=therapist,
                            day=day,
                            start_time=start_time,
                            end_time=end_time
                        )

                except ValueError as e:
                    print(f"⚠️ Skipping invalid slot format: {slot} - Error: {e}")

            return redirect('list_schedule')

    else:
        form = TherapistScheduleForm()

    return render(request, 'therapists/schedule_form.html', {'form': form})





@login_required
@user_passes_test(is_therapist)
def update_schedule(request, slot_id):
    therapist = Therapist.objects.get(account_id=request.user)
    slot = get_object_or_404(AvailableSlot, id=slot_id, therapist=therapist)

    if request.method == 'POST':
        form = TherapistScheduleForm(request.POST)

        if form.is_valid():
            selected_days = form.cleaned_data.get('available_days', [])
            selected_slots = form.cleaned_data.get('available_slots', [])

            if selected_days and selected_slots:
                slot.day = selected_days[0]  # Take the first selected day
                try:
                    time_range = selected_slots[0] if selected_slots else None
                    if time_range:
                        start_str, end_str = time_range.split('-')
                        slot.start_time = datetime.strptime(start_str, '%H:%M').time()
                        slot.end_time = datetime.strptime(end_str, '%H:%M').time()
                        slot.save()
                        return redirect('list_schedule')
                except ValueError:
                    print(f"⚠️ Invalid slot format: {time_range}")

            print("⚠️ No valid slots selected!")
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