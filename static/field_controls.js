const DATA_TYPE_CONFIG = {
  "Random Choice": {
    placeholder: "e.g. Apple,Banana,Cherry",
    validate: (value) =>
      value && value.trim() ? null : "Options cannot be empty.",
  },
  Age: {
    placeholder: "e.g. 18-65",
    validate: (value) =>
      value && /^\d+\s*-\s*\d+$/.test(value.trim())
        ? null
        : "Please enter age range as min-max (e.g. 18-65).",
  },
  Date: {
    placeholder: "e.g. %d/%b/%y",
    validate: (value) =>
      value && value.trim()
        ? null
        : "Please enter a date format (e.g. %d/%b/%y).",
  },
  "Date of Birth": {
    placeholder: "e.g. %d/%b/%y",
    validate: (value) =>
      value && value.trim()
        ? null
        : "Please enter a date format (e.g. %d/%b/%y).",
  },
  Integer: {
    placeholder: "e.g. 1-100 or 50",
    validate: (value) => {
      if (!value || !value.trim()) return null; // allow default
      if (/^\d+\s*-\s*\d+$/.test(value.trim()) || /^\d+$/.test(value.trim()))
        return null;
      return "Enter a range (min-max) or a single max value (e.g. 1-100 or 50).";
    },
  },
  Float: {
    placeholder: "e.g. 1.5-10.5 or 100",
    validate: (value) => {
      if (!value || !value.trim()) return null; // allow default
      if (
        /^\d+(\.\d+)?\s*-\s*\d+(\.\d+)?$/.test(value.trim()) ||
        /^\d+(\.\d+)?$/.test(value.trim())
      )
        return null;
      return "Enter a range (min-max) or a single max value (e.g. 1.5-10.5 or 100).";
    },
  },
  Decimal: {
    placeholder: "e.g. 1-10,3 or 4",
    validate: (value) => {
      if (!value || !value.trim()) return null; // allow default
      if (
        /^\d+(\.\d+)?\s*-\s*\d+(\.\d+)?\s*,\s*\d+$/.test(value.trim()) || // min-max,precision
        /^\d+$/.test(value.trim()) // just precision
      )
        return null;
      return "Enter range and precision (e.g. 1-10,3) or just precision (e.g. 4).";
    },
  },
  String: {
    placeholder: "e.g. 10 (length)",
    validate: (value) => {
      if (!value || !value.trim()) return null; // allow default
      if (/^\d+$/.test(value.trim())) return null;
      return "Enter a string length (e.g. 10).";
    },
  },
  // Add more data types here as needed
};

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
        optionsInput.value =
          optionsInput.getAttribute("data-original-default") || "";
        optionsInput.placeholder = "define options";
      } else {
        if (select.oldValue === "Default") {
          optionsInput.setAttribute(
            "data-original-default",
            optionsInput.value
          );
        }
        optionsInput.value = "";
        optionsInput.placeholder =
          DATA_TYPE_CONFIG[this.value]?.placeholder || "define options";
      }
      optionsInput.style.border = "";
      if (errorSpan) {
        errorSpan.style.display = "none";
        errorSpan.textContent = "";
      }
      select.oldValue = this.value;
    });
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
      let errorMsg = null;

      if (DATA_TYPE_CONFIG[select.value]?.validate) {
        errorMsg = DATA_TYPE_CONFIG[select.value].validate(optionsInput.value);
      }

      if (errorMsg) {
        valid = false;
        optionsInput.style.border = "2px solid red";
        if (errorSpan) {
          errorSpan.textContent = errorMsg;
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
