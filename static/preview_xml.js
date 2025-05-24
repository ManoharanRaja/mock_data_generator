document.addEventListener("DOMContentLoaded", function () {
  // Toggle Raw XML logic (already present)
  var toggleBtn = document.getElementById("toggle-raw-btn");
  if (toggleBtn) {
    toggleBtn.addEventListener("click", function () {
      var rawPane = document.getElementById("raw-xml-pane");
      var treePane = document.getElementById("tree-pane");
      if (rawPane.style.display !== "none") {
        rawPane.style.display = "none";
        treePane.style.flex = "1 1 100%";
        this.textContent = "Show Raw XML";
      } else {
        rawPane.style.display = "";
        treePane.style.flex = "1";
        this.textContent = "Hide Raw XML";
      }
    });
  }

  // Default option logic
  document
    .querySelectorAll("select.datatype-select")
    .forEach(function (select) {
      select.addEventListener("change", function () {
        var defaultValue = this.getAttribute("data-default-value");
        var input = this.parentElement.querySelector("input.options-input");
        if (this.value === "Default") {
          input.value = defaultValue || "";
        } else {
          // Optionally clear the input if not Default
          // input.value = "";
        }
      });
    });
});
