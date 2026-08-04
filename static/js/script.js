/* ==========================
   PROFILE DROPDOWN
========================== */

const profileBtn = document.getElementById("profileBtn");
const profileDropdown = document.getElementById("profileDropdown");

if (profileBtn && profileDropdown) {

    profileBtn.addEventListener("click", function (e) {

        e.stopPropagation();

        profileDropdown.classList.toggle("show");

    });

    document.addEventListener("click", function (e) {

        if (
            !profileBtn.contains(e.target) &&
            !profileDropdown.contains(e.target)
        ) {

            profileDropdown.classList.remove("show");

        }

    });

}


/* ==========================
   DJANGO MESSAGE POPUP
========================== */

document.addEventListener("DOMContentLoaded", function () {

    const messages =
        document.querySelectorAll(".django-message");

    messages.forEach(function (message) {

        const popup = document.createElement("div");

        popup.classList.add("alert-popup");

        const tag =
            message.dataset.tag || "";

        if (tag.includes("error")) {

            popup.classList.add("alert-error");

        }

        if (tag.includes("success")) {

            popup.classList.add("alert-success");

        }

        popup.innerText =
            message.dataset.message;

        document.body.appendChild(popup);

        setTimeout(function () {

            popup.style.opacity = "0";
            popup.style.transform =
                "translateX(100px)";

        }, 2500);

        setTimeout(function () {

            popup.remove();

        }, 3000);

    });

});


/* ==========================
   GUEST NAVBAR PROTECTION
========================== */

const authStatus =
    document.getElementById("authStatus");

if (authStatus) {

    const isLoggedIn =
        authStatus.dataset.auth;

    document
        .querySelectorAll(".protected-link")
        .forEach(function (link) {

            if (isLoggedIn === "false") {

                link.addEventListener(
                    "click",
                    function (e) {

                        e.preventDefault();

                        alert(
                            "Please login first."
                        );

                    }
                );

            }

        });

}


/* ==========================
   SCHEDULE BUTTON
========================== */

document.addEventListener("DOMContentLoaded", function () {

    const button =
        document.querySelector(".schedule-btn");

    if (!button) return;

    button.addEventListener("click", function () {

        button.innerHTML = "Loading...";

        setTimeout(function () {

            button.innerHTML =
                "View Schedule";

            document
                .getElementById("scheduleResults")
                ?.scrollIntoView({
                    behavior: "smooth",
                });

        }, 700);

    });

});


/* ==========================================================
   REUSABLE DISTRICT → UPAZILA → AREA
========================================================== */

function bindAreaCascade(
    districtId,
    upazilaId,
    areaId
) {

    const district =
        document.getElementById(districtId);

    const upazila =
        document.getElementById(upazilaId);

    const area =
        document.getElementById(areaId);

    if (!district || !upazila || !area) {
        return;
    }

    district.addEventListener("change", function () {

        upazila.innerHTML =
            `<option value="">Select Upazila</option>`;

        area.innerHTML =
            `<option value="">Select Area</option>`;

        if (!this.value) return;

        fetch(
            `/ajax/get-upazilas/?district=${encodeURIComponent(this.value)}`
        )

            .then(res => res.json())

            .then(data => {

                data.upazilas.forEach(function (item) {

                    upazila.innerHTML +=
                        `<option value="${item}">
                            ${item}
                        </option>`;

                });

            });

    });

    upazila.addEventListener("change", function () {

        area.innerHTML =
            `<option value="">Select Area</option>`;

        if (!this.value) return;

        fetch(
            `/ajax/get-areas/?district=${encodeURIComponent(district.value)}&upazila=${encodeURIComponent(this.value)}`
        )

            .then(res => res.json())

            .then(data => {

                data.areas.forEach(function (item) {

                    area.innerHTML +=
                        `<option value="${item.id}">
                            ${item.area_name}
                        </option>`;

                });

            });

    });

}

document.addEventListener("DOMContentLoaded", function () {

    bindAreaCascade(
        "district",
        "upazila",
        "area"
    );

    bindAreaCascade(
        "savedDistrict",
        "savedUpazila",
        "savedArea"
    );

});
/* ==========================
   SAVE SETUP MODAL
========================== */

document.addEventListener("DOMContentLoaded", function () {

    const openButtons = document.querySelectorAll(
        "#openSetupModal, .open-setup-modal"
    );

    const modal =
        document.getElementById("setupModal");

    const closeBtn =
        document.getElementById("closeSetupModal");

    if (!modal || openButtons.length === 0) {
        return;
    }

    openButtons.forEach(function (button) {

        button.addEventListener("click", function (event) {

            event.preventDefault();

            modal.classList.add("show");

            fetch("/users/get-saved-setup/")

                .then(function (response) {

                    return response.json();

                })

                .then(function (data) {

                    if (!data.success) {
                        return;
                    }

                    const ips =
                        document.querySelector(
                            '[name="ips_capacity"]'
                        );

                    if (ips) {
                        ips.value = data.ips_capacity;
                    }

                });

        });

    });

    if (closeBtn) {

        closeBtn.addEventListener("click", function () {

            modal.classList.remove("show");

        });

    }

    modal.addEventListener("click", function (event) {

        if (event.target === modal) {

            modal.classList.remove("show");

        }

    });

});


/* ==========================
   ADD APPLIANCE (MODAL)
========================== */

document.addEventListener("DOMContentLoaded", function () {

    const addBtn =
        document.getElementById("addAppliance");

    const container =
        document.getElementById("applianceContainer");

    if (!addBtn || !container) {
        return;
    }

    addBtn.addEventListener("click", function () {

        const firstItem =
            container.querySelector(".appliance-item");

        if (!firstItem) {
            return;
        }

        const clone =
            firstItem.cloneNode(true);

        clone.querySelectorAll("input").forEach(function (input) {

            input.value = "";

        });

        clone.querySelectorAll("select").forEach(function (select) {

            select.selectedIndex = 0;

        });

        container.appendChild(clone);

    });

});


/* ==========================================================
   SMART IPS ADVISOR
========================================================== */

document.addEventListener("DOMContentLoaded", function () {

    initializeAdvisor();

});

function initializeAdvisor() {

    setupSelection();

    applianceEvents();

    bindAnalyzeSubmit();

}
/* ==========================================================
   SETUP SELECTION
========================================================== */

function setupSelection() {

    const savedCard =
        document.getElementById("savedSetupCard");

    const tempCard =
        document.getElementById("temporarySetupCard");

    const savedSection =
        document.getElementById("savedSetupSection");

    const tempSection =
        document.getElementById("temporarySetupSection");

    const modeInput =
        document.getElementById("modeInput");

    if (
        !savedCard ||
        !tempCard ||
        !savedSection ||
        !tempSection
    ) {
        return;
    }

    const savedRequired = savedSection.querySelectorAll(
        "[name='battery_capacity']"
    );

    const tempRequired = tempSection.querySelectorAll(
        "[name='ips_capacity'],[name='battery_capacity_temp']"
    );

    function enableSaved() {

        savedCard.classList.add("active");
        tempCard.classList.remove("active");

        savedSection.classList.remove("hidden");
        tempSection.classList.add("hidden");

        if (modeInput) {
            modeInput.value = "saved";
        }

        savedRequired.forEach(input => {
            input.required = true;
        });

        tempRequired.forEach(input => {
            input.required = false;
        });

    }

    function enableTemporary() {

        tempCard.classList.add("active");
        savedCard.classList.remove("active");

        tempSection.classList.remove("hidden");
        savedSection.classList.add("hidden");

        if (modeInput) {
            modeInput.value = "temporary";
        }

        tempRequired.forEach(input => {
            input.required = true;
        });

        savedRequired.forEach(input => {
            input.required = false;
        });

    }

    enableSaved();

    savedCard.addEventListener(
        "click",
        enableSaved
    );

    tempCard.addEventListener(
        "click",
        enableTemporary
    );

}


/* ==========================================================
   APPLIANCE BUILDER
========================================================== */

function applianceEvents() {

    const addBtn =
        document.getElementById("addApplianceBtn");

    if (!addBtn) {
        return;
    }

    addBtn.addEventListener(
        "click",
        addAppliance
    );

    document.addEventListener(
        "click",
        function (event) {

            if (
                event.target.classList.contains(
                    "remove-appliance-btn"
                )
            ) {

                removeAppliance(
                    event.target
                );

            }

        }
    );

}


function addAppliance() {

    const container =
        document.getElementById(
            "applianceContainer"
        );

    if (!container) {
        return;
    }

    const firstRow =
        container.querySelector(
            ".appliance-row"
        );

    if (!firstRow) {
        return;
    }

    const clone =
        firstRow.cloneNode(true);

    clone.querySelectorAll("input")
        .forEach(function (input) {

            if (input.type === "number") {

                input.value = 1;

            } else {

                input.value = "";

            }

        });

    clone.querySelectorAll("select")
        .forEach(function (select) {

            select.selectedIndex = 0;

        });

    clone.style.opacity = "0";
    clone.style.transform =
        "translateY(15px)";

    container.appendChild(clone);

    requestAnimationFrame(function () {

        clone.style.transition = ".35s";

        clone.style.opacity = "1";

        clone.style.transform =
            "translateY(0)";

    });

}


function removeAppliance(button) {

    const rows =
        document.querySelectorAll(
            ".appliance-row"
        );

    if (rows.length <= 1) {
        return;
    }

    const row =
        button.closest(".appliance-row");

    if (!row) {
        return;
    }

    row.style.opacity = "0";

    row.style.transform =
        "translateX(40px)";

    setTimeout(function () {

        row.remove();

    }, 300);

}
/* ==========================================================
   ANALYZE BUTTON
========================================================== */

function bindAnalyzeSubmit() {

    const form =
        document.getElementById(
            "calculatorForm"
        );

    const loadingSection =
        document.getElementById(
            "loadingSection"
        );

    const analyzeSection =
        document.querySelector(
            ".analyze-section"
        );

    const dashboard =
        document.getElementById(
            "analysisDashboard"
        );

    if (!form) {
        return;
    }

    form.addEventListener(
        "submit",
        function (event) {

            if (!form.checkValidity()) {

                form.reportValidity();

                return;

            }

            event.preventDefault();

            if (analyzeSection) {

                analyzeSection.style.display =
                    "none";

            }

            if (dashboard) {

                dashboard.classList.add(
                    "hidden"
                );

            }

            if (loadingSection) {

                loadingSection.classList.remove(
                    "hidden"
                );

                loadingSection.scrollIntoView({

                    behavior: "smooth",

                    block: "center",

                });

            }

            setTimeout(function () {

                form.submit();

            }, 900);

        }

    );

}


/* ==========================================================
   RESULT ANIMATION
========================================================== */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const dashboard =
            document.getElementById(
                "analysisDashboard"
            );

        if (
            dashboard &&
            !dashboard.classList.contains(
                "hidden"
            )
        ) {

            dashboard.style.opacity = "0";

            dashboard.style.transform =
                "translateY(20px)";

            requestAnimationFrame(function () {

                dashboard.style.transition =
                    ".45s ease";

                dashboard.style.opacity = "1";

                dashboard.style.transform =
                    "translateY(0)";

            });

        }

    }
);