function toggleNav() {
    const sidenav = document.getElementById("mySidenav");
    const main = document.querySelector(".main");
    const navbar = document.querySelector(".navbar");
    const button = document.getElementById("toggleNavBtn");

    if (sidenav.style.width === "220px") {
        sidenav.style.width = "0";
        main.style.marginLeft = "0";
        navbar.style.marginLeft = "0";
    } else {
        sidenav.style.width = "220px";
        main.style.marginLeft = "220px";
        navbar.style.marginLeft = "220px";
    }
}

document.getElementById('deleteForm').addEventListener('submit', function(e) {
    e.preventDefault(); 

    const form = this;
    const url = form.action;
    const formData = new FormData(form);

    fetch(url, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        },
        body: formData
    })
    .then(response => {
        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('deleteModal'));
            modal.hide();

            window.location.href = "{{ request.build_absolute_uri|get_host }}/patients/details/{{ patient.id }}";
        } else {
            return response.json();
        }
    })
    .then(data => {
        if (data && data.error) {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});


