document.addEventListener("DOMContentLoaded", function () {
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
      // Always reset value, border, placeholder, and error message
      if (this.value === "Random Choice") {
        optionsInput.value = "";
        optionsInput.placeholder = "e.g. Apple,Banana,Cherry";
      } else {
        optionsInput.value = "";
        optionsInput.placeholder = "define options";
      }
      optionsInput.style.border = "";
      if (errorSpan) {
        errorSpan.style.display = "none";
        errorSpan.textContent = "";
      }
    });
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
          errorSpan.textContent = "Options required!";
          errorSpan.style.display = "inline";
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
