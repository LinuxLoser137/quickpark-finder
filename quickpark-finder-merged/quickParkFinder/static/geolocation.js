document.addEventListener("DOMContentLoaded", function () {
    var button = document.getElementById("use-location-btn");
    var status = document.getElementById("location-status");
    var latitudeInput = document.getElementById("latitude");
    var longitudeInput = document.getElementById("longitude");

    if (!button || !status || !latitudeInput || !longitudeInput) {
        return;
    }

    if (!("geolocation" in navigator)) {
        button.disabled = true;
        status.textContent = "Geolocation is not supported by this browser.";
        return;
    }

    button.addEventListener("click", function () {
        button.disabled = true;
        status.textContent = "Getting your location...";

        navigator.geolocation.getCurrentPosition(
            function (position) {
                var lat = position.coords.latitude;
                var lng = position.coords.longitude;
                latitudeInput.value = lat;
                longitudeInput.value = lng;
                status.textContent =
                    "Location captured (" + lat.toFixed(4) + ", " + lng.toFixed(4) + ")";
                button.disabled = false;
            },
            function (error) {
                var message;
                switch (error.code) {
                    case error.PERMISSION_DENIED:
                        message = "Location permission denied.";
                        break;
                    case error.POSITION_UNAVAILABLE:
                        message = "Location unavailable.";
                        break;
                    case error.TIMEOUT:
                        message = "Timed out getting your location.";
                        break;
                    default:
                        message = "Could not get your location.";
                }
                status.textContent = message + " You can still save without it.";
                button.disabled = false;
            },
            { enableHighAccuracy: true, timeout: 10000 }
        );
    });
});
