function initializeCalendar(config) {
    var calendarEl = document.getElementById(config.calendarId);
    var calendar = new FullCalendar.Calendar(calendarEl, {
        plugins: [FullCalendar.DayGridPlugin],
        initialView: 'dayGridMonth',
        events: config.eventsApiUrl,
    });
    calendar.render();
}

export function fetchAppointments(start, end, appointmentListEl, therapistId) {
    if (!therapistId) {
        console.error("❌ No therapist ID provided for fetching appointments");
        return;
    }

    let apiUrl = `/appointment/calendar/api/?start=${start}&end=${end}&therapist_id=${therapistId}`;
    console.log("Fetching appointments from:", apiUrl);

    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            console.log("✅ Received Appointments:", data);

            appointmentListEl.innerHTML = '';

            if (data.length === 0) {
                appointmentListEl.innerHTML = '<li class="list-group-item text-muted">No appointments found</li>';
                return;
            }

            data.forEach(appt => {
                let listItem = document.createElement('li');
                listItem.classList.add("list-group-item");
                listItem.textContent = `📅 ${appt.start.split('T')[0]} | 🕒 ${appt.start.split('T')[1].substring(0,5)}`;
                appointmentListEl.appendChild(listItem);
            });
        })
        .catch(error => {
            console.error("❌ Error fetching appointments:", error);
            appointmentListEl.innerHTML = '<li class="list-group-item text-danger">Failed to load appointments</li>';
        });
}

// NEW FUNCTION: Fetch available slots for appointment requests
export function fetchAvailableSlots(therapist_id, date, slotContainer) {
    if (!therapist_id || !date) {
        console.warn("Therapist ID or date is missing");
        return;
    }
    console.log(`🔄 Using Therapist ID: ${therapist_id} (Should match selected therapist)`);

    // Ensure date is properly formatted (YYYY-MM-DD)
    let formattedDate = new Date(date).toISOString().split('T')[0];
    let apiUrl = `/get_slots/${therapist_id}/?date=${formattedDate}`;
    console.log("Fetching available slots from:", apiUrl);

    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            console.log("Received Available Slots:", data);
            slotContainer.innerHTML = '';

            // Ensure JSON contains expected keys
            if (!data || !data.available_slots) {
                console.warn("API returned unexpected response:", data);
                slotContainer.innerHTML = '<p class="text-danger text-center">Invalid response from server</p>';
                return;
            }

            if (data.available_slots.length === 0) {
                slotContainer.innerHTML = '<p class="text-muted text-center">No available slots</p>';
            } 
            else {
                data.available_slots.forEach(slot => {
                    console.log(`Processing slot: ${slot.start_time} - ${slot.end_time}`);

                    // Ensure start_time is in HH:MM format
                    let formattedStartTime = slot.start_time.slice(0, 5); // Extracts HH:MM
                    let formattedEndTime = slot.end_time.slice(0, 5);

                    let slotBtn = document.createElement('button');
                    slotBtn.classList.add("btn", "btn-outline-success", "w-100", "my-1");
                    slotBtn.textContent = `${formattedStartTime} - ${formattedEndTime}`;
                    slotBtn.dataset.start_time = formattedStartTime;  // Ensure correct data attribute
                    slotBtn.dataset.date = formattedDate; // Store the correct date

                    console.log("Generated Slot Button:", slotBtn);  // ✅ Debugging log

                    slotBtn.onclick = function() {
                        console.log("Selected Slot:", formattedDate, formattedStartTime);
                        document.getElementById("selected_date").value = formattedDate;
                        document.getElementById("selected_time").value = formattedStartTime;
                        document.getElementById("selected_therapist").value = therapistId;
                        document.getElementById("request-appointment-btn").removeAttribute("disabled");
                    };
                    slotContainer.appendChild(slotBtn);
                });
                attachSlotClickListener();  // Attach click event after buttons are added
            }
        })
        .catch(error => {
            console.error('Error fetching available slots:', error);
            slotContainer.innerHTML = '<p class="text-danger text-center">Failed to load available slots</p>';
        });
}


export function fetchCalendarEvents(therapistId, calendar) {
    if (!therapistId) {
        console.warn("Therapist ID is missing");
        return;
    }

    let apiUrl = `/appointment/calendar/api/?therapist_id=${therapistId}`;
    console.log("Fetching appointment availability from:", apiUrl);

    fetch(apiUrl)   
        .then(response => response.json())
        .then(data => {
            console.log("Received appointment availability:", data);

            let backgroundEvents = [];
            let dateStatus = {}; 

            data.forEach(event => {
                let dateKey = event.start.split("T")[0];

                if (!dateStatus[dateKey]) {
                    dateStatus[dateKey] = {
                        date: dateKey,
                        fullyBooked: false,
                        hasAvailability: false,
                    };
                }

                if (event.extendedProps.status === "available") {
                    dateStatus[dateKey].hasAvailability = true;
                }
                if (event.extendedProps.status === "booked") {
                    dateStatus[dateKey].fullyBooked = true;
                }
            });

            // ✅ Set background colors based on availability
            Object.values(dateStatus).forEach(status => {
                backgroundEvents.push({
                    start: status.date,
                    end: status.date, // Full day
                    display: 'background',
                    color: status.fullyBooked ? "#808080" : (status.hasAvailability ? "#28a745" : "#cccccc"), 
                    title: status.fullyBooked ? "Fully Booked" : "Available",
                });
            });

            console.log("Background Events Being Sent to Calendar:", backgroundEvents);

            // ✅ Ensure calendar updates dynamically
            calendar.getEventSources().forEach(eventSource => eventSource.remove());
            calendar.addEventSource(backgroundEvents);
        })
        .catch(error => {
            console.error('Error fetching event availability:', error);
        });
}



function attachSlotClickListener() {
    document.querySelectorAll(".slot-btn").forEach(button => {
        button.addEventListener("click", function () {
            let selectedSlot = this.dataset;

            console.log("Selected Slot:", selectedSlot.date, selectedSlot.start_time);  // ✅ Debugging log

            document.getElementById("selected_date").value = selectedSlot.date;
            document.getElementById("selected_time").value = selectedSlot.start_time;
            document.getElementById("selected_therapist").value = document.getElementById("therapist").value;
            document.getElementById("request-appointment-btn").removeAttribute("disabled");

            console.log("Updated form values:", {
                date: selectedSlot.date,
                time: selectedSlot.start_time,
                therapist: document.getElementById("selected_therapist").value
            });
        });
    });

    console.log("Slot click event listeners attached.");  // ✅ Debugging log
}
