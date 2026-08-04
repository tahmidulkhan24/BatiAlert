/* ==========================
   PROFILE DROPDOWN
========================== */

const profileBtn =
document.getElementById("profileBtn");

const profileDropdown =
document.getElementById("profileDropdown");

if(profileBtn && profileDropdown){

  profileBtn.addEventListener("click", () => {
    profileDropdown.classList.toggle("show");
  });

  document.addEventListener("click", (event) => {
    if(
      !profileBtn.contains(event.target) &&
      !profileDropdown.contains(event.target)
    ){
      profileDropdown.classList.remove("show");
    }
  });
}


/* ==========================
   DJANGO MESSAGE POPUP
========================== */

document.addEventListener("DOMContentLoaded", function(){

  const messages =
  document.querySelectorAll(".django-message");

  messages.forEach(function(message){

    const text = message.dataset.message;
    const tag = message.dataset.tag;

    const popup = document.createElement("div");
    popup.classList.add("alert-popup");

    if(tag.includes("error")){
      popup.classList.add("alert-error");
    }

    if(tag.includes("success")){
      popup.classList.add("alert-success");
    }

    popup.innerText = text;
    document.body.appendChild(popup);

    setTimeout(function(){
      popup.style.opacity = "0";
      popup.style.transform = "translateX(100px)";
    }, 2500);

    setTimeout(function(){
      popup.remove();
    }, 3000);

  });

});


/* ==========================
   GUEST NAVBAR PROTECTION
========================== */

const authStatus =
document.getElementById("authStatus");

const protectedLinks =
document.querySelectorAll(".protected-link");

if(authStatus){

  const isLoggedIn = authStatus.dataset.auth;

  if(isLoggedIn === "false"){

    protectedLinks.forEach((link) => {
      link.addEventListener("click", function(event){
        event.preventDefault();
        alert("Please login first");
      });
    });

  }

}


/* ==========================
   SCHEDULE PAGE BUTTON
========================== */

document.addEventListener("DOMContentLoaded", function(){

  const button =
  document.querySelector(".schedule-btn");

  if(!button) return;

  button.addEventListener("click", function(){

    button.innerHTML = "Loading...";

    setTimeout(function(){

      button.innerHTML = "View Schedule";

      document.getElementById("scheduleResults")
      ?.scrollIntoView({ behavior:"smooth" });

    }, 700);

  });

});


/* ==========================================================
   REUSABLE DISTRICT -> UPAZILA -> AREA CASCADE
   (used by schedule.html, temporary setup, saved setup)
========================================================== */

function bindAreaCascade(districtId, upazilaId, areaId){

    const districtSelect = document.getElementById(districtId);
    const upazilaSelect = document.getElementById(upazilaId);
    const areaSelect = document.getElementById(areaId);

    if(!districtSelect || !upazilaSelect || !areaSelect){
        return;
    }

    districtSelect.addEventListener("change", function(){

        const district = this.value;

        upazilaSelect.innerHTML =
        `<option value="">Select Upazila</option>`;

        areaSelect.innerHTML =
        `<option value="">Select Area</option>`;

        if(!district){
            return;
        }

        fetch(`/ajax/get-upazilas/?district=${encodeURIComponent(district)}`)

        .then(res => res.json())

        .then(data => {

            data.upazilas.forEach(function(upazila){
                upazilaSelect.innerHTML +=
                `<option value="${upazila}">${upazila}</option>`;
            });

        });

    });

    upazilaSelect.addEventListener("change", function(){

        const district = districtSelect.value;
        const upazila = this.value;

        areaSelect.innerHTML =
        `<option value="">Select Area</option>`;

        if(!upazila){
            return;
        }

        fetch(`/ajax/get-areas/?district=${encodeURIComponent(district)}&upazila=${encodeURIComponent(upazila)}`)

        .then(res => res.json())

        .then(data => {

            data.areas.forEach(function(area){
                areaSelect.innerHTML +=
                `<option value="${area.id}">${area.area_name}</option>`;
            });

        });

    });

}

document.addEventListener("DOMContentLoaded", function(){

    // schedule.html page + calculator temporary section
    bindAreaCascade("district", "upazila", "area");

    // calculator saved setup section
    bindAreaCascade("savedDistrict", "savedUpazila", "savedArea");

});


/* ==========================
   SAVE SETUP MODAL
========================== */

document.addEventListener("DOMContentLoaded", function(){

  const openBtn = document.getElementById("openSetupModal");
  const modal = document.getElementById("setupModal");
  const closeBtn = document.getElementById("closeSetupModal");

  if(!openBtn || !modal){
    return;
  }

  openBtn.addEventListener("click", function(event){

    event.preventDefault();

    modal.classList.add("show");

    fetch("/users/get-saved-setup/")

    .then(response => response.json())

    .then(data => {

      if(!data.success){
        return;
      }

      document.querySelector('[name="ips_capacity"]').value =
      data.ips_capacity;

    });

  });

  closeBtn.addEventListener("click", function(){
    modal.classList.remove("show");
  });

  modal.addEventListener("click", function(event){
    if(event.target === modal){
      modal.classList.remove("show");
    }
  });

});


/* ==========================
   ADD APPLIANCE (MODAL - old)
========================== */

document.addEventListener("DOMContentLoaded", function(){

  const addBtn = document.getElementById("addAppliance");
  const container = document.getElementById("applianceContainer");

  if(!addBtn || !container){
    return;
  }

  addBtn.addEventListener("click", function(){

    const firstItem =
    document.querySelector(".appliance-item");

    if(!firstItem) return;

    const clone = firstItem.cloneNode(true);

    clone.querySelectorAll("input").forEach(input => {
      input.value = "";
    });

    container.appendChild(clone);

  });

});


/* ==========================================================
   SMART IPS ADVISOR (calculator page)
========================================================== */

document.addEventListener("DOMContentLoaded", () => {
    initializeAdvisor();
});


function initializeAdvisor(){
    setupSelection();
    applianceEvents();
    bindAnalyzeSubmit();
}


/* ==========================================================
   SETUP SELECTION (Saved / Temporary toggle)
========================================================== */

function setupSelection(){

    const savedCard = document.getElementById("savedSetupCard");
    const tempCard = document.getElementById("temporarySetupCard");
    const savedSection = document.getElementById("savedSetupSection");
    const tempSection = document.getElementById("temporarySetupSection");
    const modeInput = document.getElementById("modeInput");

    if(!savedCard || !tempCard){
        return;
    }

    // fields inside saved section that need "required"
    const savedRequiredFields =
    savedSection.querySelectorAll('[name="battery_capacity"]');

    // fields inside temp section that need "required"
    const tempRequiredFields =
    tempSection.querySelectorAll(
        '[name="ips_capacity"], [name="battery_capacity_temp"]'
    );

    function showSaved(){

        savedCard.classList.add("active");
        tempCard.classList.remove("active");

        savedSection.classList.remove("hidden");
        tempSection.classList.add("hidden");

        if(modeInput){
            modeInput.value = "saved";
        }

        // enable required only on visible (saved) fields
        savedRequiredFields.forEach(f => f.required = true);
        tempRequiredFields.forEach(f => f.required = false);

    }

    function showTemporary(){

        tempCard.classList.add("active");
        savedCard.classList.remove("active");

        tempSection.classList.remove("hidden");
        savedSection.classList.add("hidden");

        if(modeInput){
            modeInput.value = "temporary";
        }

        // enable required only on visible (temp) fields
        tempRequiredFields.forEach(f => f.required = true);
        savedRequiredFields.forEach(f => f.required = false);

    }

    // default state on page load
    showSaved();

    savedCard.addEventListener("click", showSaved);
    tempCard.addEventListener("click", showTemporary);

}


/* ==========================================================
   APPLIANCE BUILDER (temporary section)
========================================================== */

function applianceEvents(){

    const addBtn = document.getElementById("addApplianceBtn");

    if(!addBtn){
        return;
    }

    addBtn.addEventListener("click", addAppliance);

    document.addEventListener("click", function(e){

        if(e.target.classList.contains("remove-appliance-btn")){
            removeAppliance(e.target);
        }

    });

}


function addAppliance(){

    const container = document.getElementById("applianceContainer");
    const firstRow = container.querySelector(".appliance-row");
    const clone = firstRow.cloneNode(true);

    clone.querySelectorAll("input").forEach(input => {
        input.value = 1;
    });

    clone.style.opacity = "0";
    clone.style.transform = "translateY(15px)";

    container.appendChild(clone);

    requestAnimationFrame(() => {
        clone.style.transition = ".35s";
        clone.style.opacity = "1";
        clone.style.transform = "translateY(0)";
    });

}


function removeAppliance(button){

    const rows = document.querySelectorAll(".appliance-row");

    if(rows.length == 1){
        return;
    }

    const row = button.closest(".appliance-row");

    row.style.opacity = "0";
    row.style.transform = "translateX(40px)";

    setTimeout(() => {
        row.remove();
    }, 300);

}


/* ==========================================================
   ANALYZE SUBMIT - LOADING STATE
========================================================== */

function bindAnalyzeSubmit(){

    const form = document.getElementById("calculatorForm");
    const loadingSection = document.getElementById("loadingSection");
    const analyzeSection = document.querySelector(".analyze-section");
    const dashboard = document.getElementById("analysisDashboard");

    if(!form || !loadingSection){
        return;
    }

    form.addEventListener("submit", function(e){

        if(!form.checkValidity()){
        form.reportValidity(); // force browser to show which field is missing
        return;
    }

        e.preventDefault();

        if(analyzeSection){
            analyzeSection.style.display = "none";
        }

        if(dashboard){
            dashboard.classList.add("hidden");
        }

        loadingSection.classList.remove("hidden");

        loadingSection.scrollIntoView({
            behavior: "smooth",
            block: "center"
        });

        setTimeout(function(){
            form.submit();
        }, 900);

    });

}