// Box behaviour
document.addEventListener('DOMContentLoaded', function() {

  const boxes = document.querySelectorAll('.box');

  boxes.forEach(box => {
      const content = box.querySelector('.form-container');
      box.addEventListener('click', function() {
          boxes.forEach(b => {
              if (b !== box) {
                  b.classList.remove('expanded');
              }
          });
          box.classList.toggle('expanded');
      });

      content.addEventListener('click', function(event) {
          event.stopPropagation();
    });
  });
});


// Help text popup behaviour
document.addEventListener('DOMContentLoaded', function() {

  const questionMarks = document.querySelectorAll('.question-mark');
  let currentHelpText = null;

  questionMarks.forEach((icon) => {
    icon.addEventListener('click', function(event) {

      event.stopPropagation();

      const targetId = this.getAttribute('text-id');
      const helpText = document.getElementById(targetId);

      if (currentHelpText && currentHelpText !== helpText) {
        currentHelpText.style.display = 'none';
      }

      if (helpText.style.display === 'block') {
        helpText.style.display = 'none';
        currentHelpText = null;
      } else {
        helpText.style.display = 'block';
        currentHelpText = helpText;
      }
    });
  });
});


// Upload button behaviour
document.addEventListener('DOMContentLoaded', function() {

    const uploadBtn = document.getElementById('upload-btn');
    const pdfInput = document.getElementById('pdf-input');

    uploadBtn.addEventListener('click', function() {
        pdfInput.click();
    });

    pdfInput.addEventListener('change', function(event) {

        const file = event.target.files[0];

        if (file) {
            const formData = new FormData();
            formData.append('pdf', file);

            fetch('/upload', {
              method: 'POST',
              body: formData
            })

            .then(response => response.text())  // Expect text (HTML) instead of redirect
            .then(html => {
                document.body.innerHTML = html;  // Replace the entire body with the new response
            })

            .catch(error => {
              console.error('Error uploading file:', error);
          });
        }
    });
});


// Format digits and decimal separator on Valor Patrimonial Actual and Área
function allowOnlyDecimalNums(event) {
  const charCode = event.charCode ? event.charCode : event.keyCode;
  const input = event.target;

  // Allow digits (0-9)
  if (charCode >= 48 && charCode <= 57) {
      return true;
  }

  // Allow comma if not already present
  if (charCode === 44 && !input.value.includes(',')) {
      return true;
  }

  // Convert dot (.) to comma (,) if dot is pressed
  if (charCode === 46 && !input.value.includes(',')) {
      input.value += ','; // Add comma to the input value
      event.preventDefault(); // Prevent the dot from being entered
      return false;
  }

  // Prevent any other characters
  event.preventDefault();
  return false;
}


// Format digits on the district/county/parish input and add leading zero if user inputs only one digit
function allowOnlyDigits(event) {
  const charCode = event.charCode ? event.charCode : event.keyCode;
  if (charCode < 48 || charCode > 57) {
      event.preventDefault();
      return false;
  }
  return true;
}

function addLeadingZero(inputField) {
  if (inputField.value.length === 1) {
      inputField.value = '0' + inputField.value;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('input[name="propertyDistrict"], input[name="propertyCouncil"], input[name="propertyParish"]').forEach(input => {
      input.addEventListener('blur', function() {
          addLeadingZero(this);
      });
  });
});


// Format year field
function validateYear(input) {

  input.value = input.value.replace(/\D/g, '').slice(0, 4);

  const year = parseInt(input.value, 10);
  if (year < 1900 || year > 2024) {
      input.setCustomValidity("Insira um ano válido entre 1900 e 2024.");
  } else {
      input.setCustomValidity("");
  }
}


// Verification for valid district/council/parish codes
let validZoneCodes = [];

// Fetch valid zone codes
fetch('/zone-codes')
    .then(response => response.json())
    .then(data => {
        validZoneCodes = data;
    })
    .catch(error => console.error('Error fetching zone codes:', error));

// Validate combined code
function validateCombinedCode(district, council, parish) {
    const fullCode = district + council + parish;
    return validZoneCodes.includes(fullCode);
}

// Validate individual input field
function validateInputField(code) {
    if (validZoneCodes.length === 0) return false; // Check if validZoneCodes is empty
    return code.length === 2 && validZoneCodes.some(zone => zone.startsWith(code));
}

// Ensure the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add submit event listener to the form
    document.getElementById('input_form').addEventListener('submit', function(event) {
        const districtCode = document.getElementById('propertyDistrict');
        const councilCode = document.getElementById('propertyCouncil');
        const parishCode = document.getElementById('propertyParish');

        // Check if valid zone codes are loaded
        if (validZoneCodes.length === 0) {
            event.preventDefault(); // Prevent form submission
            alert("Zone codes are not loaded yet. Please try again later.");
            return; // Exit early
        }

        // Clear previous custom validity messages
        districtCode.setCustomValidity("");
        councilCode.setCustomValidity("");
        parishCode.setCustomValidity("");

        // Validate each input field and ensure they are filled
        let isValid = true;

        // Validate district code
        if (!districtCode.value || !validateInputField(districtCode.value)) {
            event.preventDefault(); // Prevent form submission
            districtCode.setCustomValidity("Código de distrito inválido.");
            isValid = false; // Track that validation failed
        }

        // Validate council code
        if (!councilCode.value || !validateInputField(councilCode.value)) {
            event.preventDefault(); // Prevent form submission
            councilCode.setCustomValidity("Código de concelho inválido.");
            isValid = false; // Track that validation failed
        }

        // Validate parish code
        if (!parishCode.value || !validateInputField(parishCode.value)) {
            event.preventDefault(); // Prevent form submission
            parishCode.setCustomValidity("Código de freguesia inválido.");
            isValid = false; // Track that validation failed
        }

        // Validate combined codes
        if (!validateCombinedCode(districtCode.value, councilCode.value, parishCode.value)) {
            event.preventDefault(); // Prevent form submission
            parishCode.setCustomValidity("Códigos inválidos.");
            isValid = false; // Track that validation failed
        }

        // Report validity for each input
        districtCode.reportValidity();
        councilCode.reportValidity();
        parishCode.reportValidity();

        // Check if all fields are valid
        if (!isValid) {
            event.preventDefault(); // Prevent form submission
            return; // Exit early
        }
    });
});
