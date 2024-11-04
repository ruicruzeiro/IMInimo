
// Box behaviour ---------------------------------------------------------------

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



// Help text popup behaviour ---------------------------------------------------

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



// Upload button behaviour -----------------------------------------------------

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

            .then(response => response.text())
            .then(html => {
                document.body.innerHTML = html;
            })

            .catch(error => {
              console.error('Error uploading file:', error);
          });
        }
    });
});



// Format digits and decimal separator on Valor Patrimonial Actual and Área ----

function allowOnlyDecimalNums(event) {
  const charCode = event.charCode ? event.charCode : event.keyCode;
  const input = event.target;

  if (charCode >= 48 && charCode <= 57) {
      return true;
  }

  if (charCode === 44 && !input.value.includes(',')) {
      return true;
  }

  if (charCode === 46 && !input.value.includes(',')) {
      input.value += ',';
      event.preventDefault();
      return false;
  }

  event.preventDefault();
  return false;
}



// Format digits on the zone input + add leading zero if only one digit --------

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
  document.querySelectorAll(
    'input[name="propertyDistrict"], ' +
    'input[name="propertyCouncil"], ' +
    'input[name="propertyParish"]'
  ).forEach(input => {
      input.addEventListener('blur', function() {
          addLeadingZero(this);
      });
  });
});



// Format year field -----------------------------------------------------------

function validateYear(input) {

  input.value = input.value.replace(/\D/g, '').slice(0, 4);

  const year = parseInt(input.value, 10);
  if (year < 1900 || year > 2024) {
      input.setCustomValidity("Insira um ano válido entre 1900 e 2024.");
  } else {
      input.setCustomValidity("");
  }
}



// Verification for valid zone codes -------------------------------------------

document.addEventListener('DOMContentLoaded', function() {

  const form = document.getElementById('input-form');
  const districtInput = document.getElementsByName('propertyDistrict')[0];
  const councilInput = document.getElementsByName('propertyCouncil')[0];
  const parishInput = document.getElementsByName('propertyParish')[0];

  let zoneCodes = [];

  fetch('/zone-codes')
      .then(response => response.json())
      .then(data => {
          zoneCodes = data;
      })
      .catch(error => {
          console.error('Error fetching zone codes:', error);
          alert('Error loading zone codes. Please refresh the page.');
      });

  form.addEventListener('submit', function(event) {
      event.preventDefault();

      const district = districtInput.value;
      const council = councilInput.value;
      const parish = parishInput.value;
      const fourDigitCode = district + council;
      const sixDigitCode = district + council + parish;

      if (zoneCodes.includes(fourDigitCode) || zoneCodes.includes(sixDigitCode)) {
          form.submit();
      } else {
          parishInput.setCustomValidity("Código inválido. Verifique os três campos de distrito, concelho e freguesia.");
          parishInput.reportValidity();
      }
  });

  [districtInput, councilInput, parishInput].forEach(input => {
      input.addEventListener('input', function() {
          parishInput.setCustomValidity("");
      });
  });
});
