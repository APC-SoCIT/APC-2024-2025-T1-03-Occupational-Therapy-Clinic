function initializeCalendar(config) {
    var calendarEl = document.getElementById(config.calendarId);
    var calendar = new FullCalendar.Calendar(calendarEl, {
        plugins: [FullCalendar.DayGridPlugin],
        initialView: 'dayGridMonth',
        events: config.eventsApiUrl,
    });
    calendar.render();
}

export function fetchAppointments(start, end, appointmentListEl) {
    fetch(`api/?start=${start}&end=${end}`)
        .then(response => response.json())
        .then(appointments => {
            // Clear existing list
            appointmentListEl.innerHTML = '';

            if (appointments.length === 0) {
                appointmentListEl.innerHTML = '<li class="list-group-item">No appointments for the selected period</li>';
            } else {
                appointments.forEach(appt => {
                    const listItem = document.createElement('li');
                    listItem.classList.add('list-group-item');
                    listItem.innerHTML = `
                        <strong>${appt.title}</strong>
                        <br>
                        Start: ${new Date(appt.start).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        <br>
                        End: ${new Date(appt.end).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    `;
                    appointmentListEl.appendChild(listItem);
                });
            }
        })
        .catch(error => {
            console.error('Error fetching appointments:', error);
            appointmentListEl.innerHTML = '<li class="list-group-item text-danger">Failed to load appointments</li>';
        });
}

