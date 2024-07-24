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
  inputsElement.forEach((input) => {
    input.value = input.id;
  });
}

// function uploadToStorage(userData) {
//   localStorage.clear();
//   const userDataJson = JSON.stringify(userData);

//   localStorage.setItem("user_input", userDataJson);
// }

// document
//   .querySelector(".submit-button")
//   .addEventListener("click", function (e) {
//     e.preventDefault();
//     const userData = getUserInput();
//     uploadToStorage(userData);
//     console.log("User Data:", userData);
//   });

// // Uncomment the line below for testing purposes
testFillInput();
