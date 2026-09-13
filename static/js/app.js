/* MediVault EHR - vanilla JavaScript helpers (no frameworks). */
(function () {
  "use strict";

  // ---- Auto dismiss alerts after 6 seconds -------------------------------
  document.addEventListener("DOMContentLoaded", function () {
    setTimeout(function () {
      document.querySelectorAll(".mv-messages .alert").forEach(function (el) {
        el.classList.remove("show");
        setTimeout(function () { el.remove(); }, 300);
      });
    }, 6000);
  });

  // ---- Confirm dangerous actions -----------------------------------------
  document.addEventListener("click", function (event) {
    var target = event.target.closest("[data-confirm]");
    if (target && !window.confirm(target.getAttribute("data-confirm"))) {
      event.preventDefault();
    }
  });

  // ---- Dynamic medicine rows for the prescription form -------------------
  window.MediVaultFormset = {
    init: function (prefix) {
      var container = document.getElementById("medicine-rows");
      var addButton = document.getElementById("add-medicine");
      var totalForms = document.getElementById("id_" + prefix + "-TOTAL_FORMS");
      var emptyTemplate = document.getElementById("empty-medicine-form");
      if (!container || !addButton || !totalForms || !emptyTemplate) { return; }

      addButton.addEventListener("click", function () {
        var index = parseInt(totalForms.value, 10);
        var html = emptyTemplate.innerHTML.replace(/__prefix__/g, index);
        var wrapper = document.createElement("div");
        wrapper.innerHTML = html;
        container.appendChild(wrapper.firstElementChild);
        totalForms.value = index + 1;
      });

      container.addEventListener("click", function (event) {
        var removeBtn = event.target.closest(".remove-medicine");
        if (!removeBtn) { return; }
        var row = removeBtn.closest(".medicine-row");
        var deleteInput = row.querySelector("input[type=checkbox][name$='-DELETE']");
        if (deleteInput) {
          // Existing medicine: flag it for deletion and hide the row.
          deleteInput.checked = true;
          row.style.display = "none";
        } else {
          row.remove();
        }
      });
    }
  };
})();
