function getUserInput() {
  const inputsElement = document.querySelectorAll("input");
  const selectsElement = document.querySelectorAll("select");
  const data = {};

  inputsElement.forEach((input) => {
    data[input.id] = input.value;

    if (input.type === "checkbox") {
      data[input.id] = input.checked;
    }
  });

  selectsElement.forEach((input) => {
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
    outputFilePath:
      "C:\\Users\\ibrah\\OneDrive\\Documents\\Projects\\life_cf_app\\output",
    outputFileName: "pricing_model_py_output",
  };

  inputsElement.forEach((input) => {
    input.value = testInput[input.id];
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  const runButton = document.querySelector("#run-script-icon");
  const dirname = await window.electronAPI.getDirname();

  // Display python log messages received from main-process via 'python-log' channel.
  window.electronAPI.onPythonLog((event, log) => {
    const logWrapper = document.querySelector(".log-wrapper");
    const logLines = log.split("\r\n");
    logLines.forEach((line) => {
      if (line.trim() !== "") {
        // Ignore empty lines
        const logDiv = document.createElement("div");
        logDiv.classList.add("py-log");
        logDiv.textContent = line;
        logWrapper.appendChild(logDiv);
      }
    });
  });

  // Add event listener to run python script
  // Approach: Get user input in html -> create json file -> python read json file
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

    // Initialise log section for logging
    const logWrapper = document.querySelector(".log-wrapper");
    logWrapper.textContent = "Running Python ...";

    // Run python script
    try {
      const result = await window.electronAPI.runPythonScript(jsonFilePath);
      if (result.success) {
        // add py-log child
        const logDiv = document.createElement("div");
        logDiv.classList.add("py-log");
        logDiv.textContent = "Script completed successfully!";
        logWrapper.appendChild(logDiv);
      } else {
        logWrapper.textContent += `Error: ${result.error}\n`;
      }
    } catch (error) {
      logWrapper.textContent += `Error running Python script: ${error}\n`;
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
