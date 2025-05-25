document.addEventListener("DOMContentLoaded", function () {
  // Store default values for each options input
  document.querySelectorAll(".data-type-select").forEach(function (select) {
    var field = select.getAttribute("data-field");
    var optionsInput = document.querySelector(
      'input.options-input[data-field="' + field + '"]'
    );
    if (optionsInput) {
      optionsInput.setAttribute("data-original-default", optionsInput.value);
    }
  });

  // Reset options field on data type change
  document.querySelectorAll(".data-type-select").forEach(function (select) {
    select.addEventListener("change", function () {
      var field = this.getAttribute("data-field");
      var optionsInput = document.querySelector(
        'input.options-input[data-field="' + field + '"]'
      );
      var errorSpan = document.querySelector(
        'span.options-error[data-field="' + field + '"]'
      );
      if (!optionsInput) return;

      if (this.value === "Default") {
        // Restore the original default value
        optionsInput.value =
          optionsInput.getAttribute("data-original-default") || "";
        optionsInput.placeholder = "define options";
      } else {
        // Before switching away from Default, update the stored default value
        if (select.oldValue === "Default") {
          optionsInput.setAttribute(
            "data-original-default",
            optionsInput.value
          );
        }
        optionsInput.value = "";
        if (this.value === "Random Choice") {
          optionsInput.placeholder = "e.g. Apple,Banana,Cherry";
        } else {
          optionsInput.placeholder = "define options";
        }
      }
      optionsInput.style.border = "";
      if (errorSpan) {
        errorSpan.style.display = "none";
        errorSpan.textContent = "";
      }
      select.oldValue = this.value; // Track previous value
    });
    // Initialize oldValue for each select
    select.oldValue = select.value;
  });

  // Validation on form submit
  document.querySelector("form").addEventListener("submit", function (e) {
    let valid = true;
    document.querySelectorAll(".data-type-select").forEach(function (select) {
      var field = select.getAttribute("data-field");
      var optionsInput = document.querySelector(
        'input.options-input[data-field="' + field + '"]'
      );
      var errorSpan = document.querySelector(
        'span.options-error[data-field="' + field + '"]'
      );
      if (
        select.value === "Random Choice" &&
        (!optionsInput.value || !optionsInput.value.trim())
      ) {
        valid = false;
        optionsInput.style.border = "2px solid red";
        if (errorSpan) {
          errorSpan.textContent = "Options cannot be empty.";
          errorSpan.style.display = "inline";
          errorSpan.style.color = "red";
        }
      } else {
        optionsInput.style.border = "";
        if (errorSpan) {
          errorSpan.textContent = "";
          errorSpan.style.display = "none";
        }
      }
    });
    if (!valid) {
      e.preventDefault();
    }
  });
});
