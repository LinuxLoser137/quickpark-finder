// QuickPark Finder inactivity timeout
// Automatically logs the user out after 15 minutes
// without mouse, keyboard, touch, click, or scroll activity.

const INACTIVITY_LIMIT = 15 * 60 * 1000;

let inactivityTimer;

function logoutUser() {
    window.location.href = "/auth/logout";
}

function resetInactivityTimer() {
    clearTimeout(inactivityTimer);

    inactivityTimer = setTimeout(
        logoutUser,
        INACTIVITY_LIMIT
    );
}

document.addEventListener("mousemove", resetInactivityTimer);
document.addEventListener("mousedown", resetInactivityTimer);
document.addEventListener("keydown", resetInactivityTimer);
document.addEventListener("touchstart", resetInactivityTimer);
document.addEventListener("scroll", resetInactivityTimer);

resetInactivityTimer();
