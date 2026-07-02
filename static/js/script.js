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

    const openButtons =
    document.querySelectorAll(
      "#openSetupModal, .open-setup-modal"
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
      !openButtons.length ||
      !modal
    ){
      return;
    }

    openButtons.forEach(
      function(openBtn){

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
