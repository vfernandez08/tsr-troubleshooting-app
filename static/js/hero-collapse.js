// Hero collapse functionality for returning users
document.addEventListener('DOMContentLoaded', function() {
    // Check if hero was previously dismissed
    if (localStorage.getItem("heroDismissed")) {
        const hero = document.querySelector(".hero");
        if (hero) {
            hero.style.display = "none";
        }
    }

    // Add dismiss functionality
    const dismissBtn = document.querySelector("#dismiss-hero");
    if (dismissBtn) {
        dismissBtn.addEventListener("click", function() {
            const hero = document.querySelector(".hero");
            if (hero) {
                hero.style.display = "none";
                localStorage.setItem("heroDismissed", "1");
            }
        });
    }
});