document.addEventListener("DOMContentLoaded", function () {
    var consentModal = new bootstrap.Modal(document.getElementById('consentModal'));
    consentModal.show();

    document.getElementById("agreeBtn").addEventListener("click", function () {
        consentModal.hide();
    });

});