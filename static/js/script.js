/* ==========================
   PROFILE DROPDOWN
========================== */

const profileBtn =
document.getElementById(
  "profileBtn"
);

const profileDropdown =
document.getElementById(
  "profileDropdown"
);

/* only if profile exists */
if(profileBtn && profileDropdown){

  profileBtn.addEventListener(
    "click",
    () => {

      profileDropdown.classList.toggle(
        "show"
      );

    }
  );

  document.addEventListener(
    "click",
    (event) => {

      if(
        !profileBtn.contains(
          event.target
        )
        &&
        !profileDropdown.contains(
          event.target
        )
      ){

        profileDropdown.classList.remove(
          "show"
        );

      }

    }
  );
}


/* ==========================
   DJANGO MESSAGE POPUP
========================== */

document.addEventListener(
  "DOMContentLoaded",
  function(){

    const messages =
    document.querySelectorAll(
      ".django-message"
    );

    messages.forEach(
      function(message){

        const text =
        message.dataset.message;

        const tag =
        message.dataset.tag;

        const popup =
        document.createElement(
          "div"
        );

        popup.classList.add(
          "alert-popup"
        );

        if(tag.includes("error")){
          popup.classList.add(
            "alert-error"
          );
        }

        if(tag.includes("success")){
          popup.classList.add(
            "alert-success"
          );
        }

        popup.innerText =
        text;

        document.body.appendChild(
          popup
        );

        setTimeout(
          function(){

            popup.style.opacity =
            "0";

            popup.style.transform =
            "translateX(100px)";

          },
          2500
        );

        setTimeout(
          function(){

            popup.remove();

          },
          3000
        );

      }
    );
  }
);
/* ==========================
   GUEST NAVBAR PROTECTION
========================== */

const authStatus =
document.getElementById(
  "authStatus"
);

const protectedLinks =
document.querySelectorAll(
  ".protected-link"
);

if(authStatus){

  const isLoggedIn =
  authStatus.dataset.auth;

  if(isLoggedIn === "false"){

    protectedLinks.forEach(
      (link)=>{

        link.addEventListener(
          "click",
          function(event){

            event.preventDefault();

            alert(
              "Please login first"
            );

          }
        );

      }
    );

  }

}
/* ==========================
   SCHEDULE PAGE
========================== */

document.addEventListener(
  "DOMContentLoaded",
  function(){

    const button =
    document.querySelector(
      ".schedule-btn"
    );

    if(!button) return;

    button.addEventListener(
      "click",
      function(){

        button.innerHTML =
        "Loading...";

        setTimeout(
          function(){

            button.innerHTML =
            "View Schedule";

            document
            .getElementById(
              "scheduleResults"
            )
            ?.scrollIntoView({
              behavior:"smooth"
            });

          },
          700
        );

      }
    );

  }
);
/* ==========================
   AJAX SCHEDULE FILTER
========================== */

document.addEventListener(
  "DOMContentLoaded",
  function(){

    const districtSelect =
    document.getElementById(
      "district"
    );

    const upazilaSelect =
    document.getElementById(
      "upazila"
    );

    const areaSelect =
    document.getElementById(
      "area"
    );

    if(
      !districtSelect ||
      !upazilaSelect ||
      !areaSelect
    ){
      return;
    }

    districtSelect.addEventListener(
      "change",
      function(){

        const district =
        this.value;

        fetch(
          `/ajax/get-upazilas/?district=${district}`
        )

        .then(
          response =>
          response.json()
        )

        .then(
          data => {

            upazilaSelect.innerHTML =
            `
            <option value="">
            Select Upazila
            </option>
            `;

            areaSelect.innerHTML =
            `
            <option value="">
            Select Area
            </option>
            `;

            data.upazilas.forEach(
              function(upazila){

                upazilaSelect.innerHTML +=
                `
                <option value="${upazila}">
                ${upazila}
                </option>
                `;

              }
            );

          }
        );

      }
    );

    upazilaSelect.addEventListener(
      "change",
      function(){

        const district =
        districtSelect.value;

        const upazila =
        this.value;

        fetch(
          `/ajax/get-areas/?district=${district}&upazila=${upazila}`
        )

        .then(
          response =>
          response.json()
        )

        .then(
          data => {

            areaSelect.innerHTML =
            `
            <option value="">
            Select Area
            </option>
            `;

            data.areas.forEach(
              function(area){

                areaSelect.innerHTML +=
                `
                <option value="${area.id}">
                ${area.area_name}
                </option>
                `;

              }
            );

          }
        );

      }
    );

  }
);
/* ==========================
   SAVE SETUP MODAL
========================== */

document.addEventListener(
  "DOMContentLoaded",
  function(){

    const openBtn =
    document.getElementById(
      "openSetupModal"
    );

    const modal =
    document.getElementById(
      "setupModal"
    );

    const closeBtn =
    document.getElementById(
      "closeSetupModal"
    );

    if(
      !openBtn ||
      !modal
    ){
      return;
    }

    openBtn.addEventListener(
      "click",
      function(event){

        event.preventDefault();

        modal.classList.add(
          "show"
        );
       fetch(
            "/users/get-saved-setup/"
          )

          .then(
            response =>
            response.json()
          )

          .then(
            data => {

              if(
                !data.success
              ){
                return;
              }

              document.querySelector(
                '[name="ips_capacity"]'
              ).value =
              data.ips_capacity;

            }
          );
                }
    );

    closeBtn.addEventListener(
      "click",
      function(){

        modal.classList.remove(
          "show"
        );

      }
    );

    modal.addEventListener(
      "click",
      function(event){

        if(
          event.target === modal
        ){

          modal.classList.remove(
            "show"
          );

        }

      }
    );

  }
);
/* ==========================
   ADD APPLIANCE
========================== */

document.addEventListener(
  "DOMContentLoaded",
  function(){

    const addBtn =
    document.getElementById(
      "addAppliance"
    );

    const container =
    document.getElementById(
      "applianceContainer"
    );

    if(
      !addBtn ||
      !container
    ){
      return;
    }

    addBtn.addEventListener(
      "click",
      function(){

        const firstItem =
        document.querySelector(
          ".appliance-item"
        );

        const clone =
        firstItem.cloneNode(
          true
        );

        clone
        .querySelectorAll(
          "input"
        )
        .forEach(
          input =>
          input.value = ""
        );

        container.appendChild(
          clone
        );

      }
    );

  }
);
/* ==========================================================
   SMART IPS ADVISOR
========================================================== */

document.addEventListener("DOMContentLoaded", () => {

    initializeAdvisor();

});


/* ==========================================================
   DEMO DATA
========================================================== */

const appliancePower = {

    "LED Light": 12,
    "Fan": 75,
    "Television": 90,
    "WiFi Router": 15,
    "Laptop": 65,
    "Desktop PC": 220,
    "Refrigerator": 180,
    "Rice Cooker": 700,
    "Air Cooler": 180

};

const scheduleDemo = [

    {

        area:"Mohammadpur",

        hasSchedule:true,

        start:"2:00 PM",

        end:"4:00 PM",

        duration:"2 Hours"

    },

    {

        area:"Mirpur",

        hasSchedule:false

    }

];


/* ==========================================================
   INITIALIZE
========================================================== */

function initializeAdvisor(){

    setupSelection();

    applianceEvents();

    analyzeEvent();

}


/* ==========================================================
   SETUP SELECTION
========================================================== */

function setupSelection(){

    const savedCard=document.getElementById("savedSetupCard");

    const tempCard=document.getElementById("temporarySetupCard");

    const savedSection=document.getElementById("savedSetupSection");

    const tempSection=document.getElementById("temporarySetupSection");


    savedCard.addEventListener("click",()=>{

        savedCard.classList.add("active");

        tempCard.classList.remove("active");

        savedSection.classList.remove("hidden");

        tempSection.classList.add("hidden");

    });


    tempCard.addEventListener("click",()=>{

        tempCard.classList.add("active");

        savedCard.classList.remove("active");

        tempSection.classList.remove("hidden");

        savedSection.classList.add("hidden");

    });

}


/* ==========================================================
   APPLIANCE BUILDER
========================================================== */

function applianceEvents(){

    const addBtn=document.getElementById("addApplianceBtn");

    if(!addBtn) return;

    addBtn.addEventListener("click",addAppliance);

    document.addEventListener("click",(e)=>{

        if(e.target.classList.contains("remove-appliance-btn")){

            removeAppliance(e.target);

        }

    });

}


function addAppliance(){

    const container=document.getElementById("applianceContainer");

    const row=document.createElement("div");

    row.className="appliance-row";

    row.innerHTML=`

        <div class="form-group">

            <label class="form-label">

                Appliance

            </label>

            <select class="form-input appliance-select">

                <option>LED Light</option>

                <option>Fan</option>

                <option>Television</option>

                <option>WiFi Router</option>

                <option>Laptop</option>

                <option>Desktop PC</option>

                <option>Refrigerator</option>

                <option>Rice Cooker</option>

                <option>Air Cooler</option>

            </select>

        </div>

        <div class="form-group">

            <label class="form-label">

                Quantity

            </label>

            <input
                type="number"
                class="form-input quantity-input"
                value="1"
                min="1">

        </div>

        <div class="form-group">

            <label class="form-label">

                Priority

            </label>

            <select class="form-input">

                <option>High</option>

                <option>Medium</option>

                <option>Low</option>

            </select>

        </div>

        <button
            type="button"
            class="remove-appliance-btn">

            Remove

        </button>

    `;

    row.style.opacity="0";

    row.style.transform="translateY(15px)";

    container.appendChild(row);

    requestAnimationFrame(()=>{

        row.style.transition=".35s";

        row.style.opacity="1";

        row.style.transform="translateY(0)";

    });

}


function removeAppliance(button){

    const row=button.closest(".appliance-row");

    row.style.opacity="0";

    row.style.transform="translateX(40px)";

    setTimeout(()=>{

        row.remove();

    },300);

}


/* ==========================================================
   ANALYZE BUTTON
========================================================== */

function analyzeEvent(){

    const btn=document.getElementById("analyzeBtn");

    if(!btn) return;

    btn.addEventListener("click",analyzeIPS);

}


function analyzeIPS(){

    const loading=document.getElementById("loadingSection");

    const dashboard=document.getElementById("analysisDashboard");

    loading.classList.remove("hidden");

    dashboard.classList.add("hidden");

    setTimeout(()=>{

        loading.classList.add("hidden");

        dashboard.classList.remove("hidden");

        runCalculation();

    },1000);

}
/* ==========================================================
   CALCULATION ENGINE
========================================================== */

function runCalculation(){

    const totalLoad = calculateLoad();

    const batteryHours = calculateBackup(totalLoad);

    updateSummary(totalLoad,batteryHours);

    updateSchedule();

    generateRecommendation(totalLoad,batteryHours);

}


/* ==========================================================
   LOAD CALCULATION
========================================================== */

function calculateLoad(){

    const rows=document.querySelectorAll(".appliance-row");

    let total=0;

    rows.forEach(row=>{

        const appliance=row.querySelector(".appliance-select").value;

        const quantity=parseInt(
            row.querySelector(".quantity-input").value
        )||1;

        const watt=appliancePower[appliance]||0;

        total+=watt*quantity;

    });

    return total;

}


/* ==========================================================
   BACKUP CALCULATION
========================================================== */

function calculateBackup(load){

    const batteryAh=150;

    const batteryVoltage=12;

    const efficiency=.85;

    const batteryWh=batteryAh*batteryVoltage;

    const usable=batteryWh*efficiency;

    return usable/load;

}


/* ==========================================================
   UPDATE SUMMARY
========================================================== */

function updateSummary(load,hours){

    document.getElementById("totalLoad").textContent=
        Math.round(load)+" W";

    document.getElementById("summaryLoad").textContent=
        Math.round(load)+" W";

    document.getElementById("backupTime").textContent=
        hours.toFixed(1)+" Hours";

    document.getElementById("summaryRuntime").textContent=
        hours.toFixed(1)+" H";

    document.getElementById("batteryBackup").textContent=
        convertHour(hours);

    document.getElementById("summaryBattery").textContent=
        "150 Ah";

    document.getElementById("summaryAppliance").textContent=
        document.querySelectorAll(".appliance-row").length;

    updateStatus(hours);

    animateBattery(hours);

}


/* ==========================================================
   READY / WARNING / DANGER
========================================================== */

function updateStatus(hours){

    const badge=document.getElementById("backupStatus");

    badge.className="status-badge";

    if(hours>=5){

        badge.classList.add("ready");

        badge.textContent="READY";

    }

    else if(hours>=3){

        badge.classList.add("warning");

        badge.textContent="Needs Optimization";

    }

    else{

        badge.classList.add("danger");

        badge.textContent="Backup Not Enough";

    }

}


/* ==========================================================
   TODAY'S SCHEDULE (Demo)
========================================================== */

function updateSchedule(){

    const demo=scheduleDemo[
        Math.floor(
            Math.random()*scheduleDemo.length
        )
    ];

    document.getElementById("resultArea").textContent=
        demo.area;

    const status=document.getElementById("scheduleStatus");

    if(demo.hasSchedule){

        document.getElementById("startTime").textContent=
            demo.start;

        document.getElementById("endTime").textContent=
            demo.end;

        document.getElementById("duration").textContent=
            demo.duration;

        status.textContent="Scheduled Today";

        status.className="schedule-status success";

    }

    else{

        document.getElementById("startTime").textContent="-";

        document.getElementById("endTime").textContent="-";

        document.getElementById("duration").textContent="-";

        status.textContent="No Scheduled Load Shedding";

        status.className="schedule-status warning";

    }

}
/* ==========================================================
   RECOMMENDATION ENGINE
========================================================== */

function generateRecommendation(load, hours){

    const cards = document.querySelectorAll(".recommend-card");

    const optimized = document.querySelector(".optimized-result h2");

    cards.forEach(card => card.style.display = "none");

    if(hours >= 5){

        cards[0].style.display = "none";
        cards[1].style.display = "none";
        cards[2].style.display = "none";

        optimized.innerText =
            "Your current setup is already optimized.";

        return;

    }

    if(load >= 500){

        cards[0].style.display = "block";
        cards[1].style.display = "block";
        cards[2].style.display = "block";

        optimized.innerText =
            convertHour(hours + 2);

    }

    else if(load >= 300){

        cards[0].style.display = "block";
        cards[1].style.display = "block";

        optimized.innerText =
            convertHour(hours + 1);

    }

    else{

        cards[0].style.display = "block";

        optimized.innerText =
            convertHour(hours + .5);

    }

}


/* ==========================================================
   BATTERY GAUGE
========================================================== */

function animateBattery(hours){

    let percent = Math.round((hours / 8) * 100);

    if(percent > 100){

        percent = 100;

    }

    if(percent < 5){

        percent = 5;

    }

    document.getElementById("batteryPercent").innerText =
        percent + "%";

    const degree = percent * 3.6;

    const circle = document.querySelector(".battery-circle");

    circle.style.background = `

        conic-gradient(

            #3f8cff 0deg,

            #3f8cff ${degree}deg,

            rgba(255,255,255,.08) ${degree}deg,

            rgba(255,255,255,.08) 360deg

        )

    `;

}


/* ==========================================================
   HOUR TO TEXT
========================================================== */

function convertHour(hour){

    const h = Math.floor(hour);

    const m = Math.round((hour - h) * 60);

    if(h <= 0){

        return m + " Minutes";

    }

    if(m === 0){

        return h + " Hours";

    }

    return h + " Hours " + m + " Minutes";

}


/* ==========================================================
   OPTIONAL RANDOM DATA
========================================================== */

function randomBattery(){

    return Math.floor(Math.random() * 41) + 120;

}

function randomVoltage(){

    const list = [12,24,48];

    return list[Math.floor(Math.random()*list.length)];

}


/* ==========================================================
   SMALL FADE EFFECT
========================================================== */

function revealDashboard(){

    const dashboard = document.getElementById("analysisDashboard");

    dashboard.style.opacity = 0;

    dashboard.style.transform = "translateY(20px)";

    requestAnimationFrame(()=>{

        dashboard.style.transition = ".5s";

        dashboard.style.opacity = 1;

        dashboard.style.transform = "translateY(0)";

    });

}


/* ==========================================================
   MODIFY analyzeIPS()
========================================================== */

/*
Inside analyzeIPS()

Replace

runCalculation();

with

runCalculation();
revealDashboard();

*/


/* ==========================================================
   END OF SMART IPS ADVISOR
========================================================== */