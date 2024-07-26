function getUserInput() {
  const inputsElement = document.querySelectorAll("input");
  const data = {};

  inputsElement.forEach((input) => {
    data[input.id] = input.value;
  });

  return data;
}

function testFillInput() {
  // use this function to temporarily fill the input for testing purposes
  const inputsElement = document.querySelectorAll("input");
  const testInput = {
    filePath:
      "C:\\Users\\ibrah\\OneDrive\\Documents\\Projects\\life_cashflow_app\\resources\\pricing_model.xlsx",
    age: "Age",
    gender: "Gender",
    polYear: "Pol_Year",
    sumAssured: "SumAssured",
    contributionPerYear: "Contribution_perYear",
    surplusShareToParticipant: "SurplusShare_toParticipant",
    surplusShareToShf: "SurplusShare_toSHF",
    tabWakalahFee: "Tab_WakalahFee",
    wakalahFmc: "Wakalah_Thrarawat",
    coiLoading: "COI_Loading",
    expensePerContributionPerYear: "Expense_perContribution_perYear",
    expensePerFundPerYear: "Expense_perFund_perYear",
    tabMortalityRates: "Tab_MortalityRates",
    tabLapseRate: "Tab_LapseRate",
    tabRiskFreeRates: "Tab_RiskFreeRates",
  };

  inputsElement.forEach((input) => {
    input.value = testInput[input.id];
  });
}

// Add event listener to run python script
// Approach: Get user input in html -> create json file -> python read json file
document.addEventListener("DOMContentLoaded", async () => {
  const runButton = document.querySelector("#run-script-icon");
  const dirname = await window.electronAPI.getDirname();

  runButton.addEventListener("click", async () => {
    // Get user input
    const user_input = getUserInput();

    // Define JSON path
    const jsonFilePath = `${dirname}/user_input.json`;

    // Write user input to JSON file
    await window.electronAPI.writeJsonFile(
      jsonFilePath,
      JSON.stringify(user_input, null, 2)
    );

    // Run python script
    try {
      const result = await window.electronAPI.runPythonScript(jsonFilePath);
      console.log(result);
    } catch (error) {
      console.error("Error running Python script:", error);
      document.getElementById("output").textContent =
        "Error occurred. Check console for details.";
    }
  });
});

// Fill the input field for testing. Commented if not in use.
testFillInput();

document.addEventListener("DOMContentLoaded", function () {
  const navItems = document.querySelectorAll(".nav-item-wrapper");
  const navIcon = document.querySelectorAll(".nav-item-wrapper img");
  const sections = document.querySelectorAll(".section");

  navItems.forEach((item) => {
    item.addEventListener("click", function (event) {
      event.preventDefault();
      const targetId = event.target.id.replace("-icon", "");
      showSection(targetId);
    });
  });

  function showSection(targetId) {
    // Remove active class from all nav items
    navItems.forEach((item) => {
      item.classList.remove("active");
    });

    // Remove select-style from all nav icon
    navIcon.forEach((item) => {
      item.style.borderBottom = "";
    });

    // Hide all sections and remove flex class
    sections.forEach((section) => {
      section.classList.remove("active");
      section.style.display = "none";
    });

    // Add active class to the clicked nav item
    document.getElementById(targetId).classList.add("active");

    // Add style to active nav icon
    document.querySelector(".nav-item-wrapper.active img").style.borderBottom =
      "5px solid #ffffff";

    // Show the target section and add flex class
    document
      .querySelector(".section#" + targetId + "-wrapper")
      .classList.add("active");
    document.querySelector(".section#" + targetId + "-wrapper").style.display =
      "unset";
  }

  // Initial display setup - show the home section
  showSection("home");
});
