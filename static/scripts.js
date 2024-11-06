
// Box behaviour ---------------------------------------------------------------

document.addEventListener('DOMContentLoaded', function() {

  const boxes = document.querySelectorAll('.box');

  boxes.forEach(box => {

    if (box.classList.contains('single-box')) {
      return; // Skip this box if it's also a single-box
    }

    const content = box.querySelector('.form-container');
    box.addEventListener('click', function() {
        boxes.forEach(b => {
            if (b !== box) {
                b.classList.remove('expanded');
            }
        });
        box.classList.toggle('expanded');
    });

    if (content) {
      content.addEventListener('click', function(event) {
          event.stopPropagation();
      });
    }
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
  // Only run if the current page is index.html or the index route
  if (window.location.pathname === '/index' || window.location.pathname === '/index.html' || window.location.pathname === '/') {

    const uploadBtn = document.getElementById('upload-btn');
    const pdfInput = document.getElementById('pdf-input');
    const box = document.querySelector('.box[style*="background-color: #483D8B"]');
    const zoneCoefInput = document.createElement('input');
    const confirmBtn = document.createElement('button');

    const instructionH4 = document.createElement('h4');
    instructionH4.style.display = 'none';
    instructionH4.innerHTML = '<br><br>O coeficiente de localização da sua Caderneta pode ter sofrido alterações. Encontre o mais recente <a href="https://zonamentopf.portaldasfinancas.gov.pt/simulador/default.jsp" target="_blank">neste mapa</a> e clique em Confirmar.';

    // Set up the new input field for zone_coef
    zoneCoefInput.setAttribute('type', 'text');
    zoneCoefInput.setAttribute('id', 'Cl');
    zoneCoefInput.setAttribute('placeholder', 'Coeficiente de Localização');
    zoneCoefInput.style.padding = '5px';
    zoneCoefInput.style.marginBottom = '15px';
    zoneCoefInput.style.border = '1px solid #ccc';
    zoneCoefInput.style.borderRadius = '4px';
    zoneCoefInput.style.fontSize = '16px';
    zoneCoefInput.style.width = '100px';
    zoneCoefInput.style.boxSizing = 'border-box';
    zoneCoefInput.style.outline = 'none';
    zoneCoefInput.style.height = '30px';
    zoneCoefInput.style.marginTop = '20px';
    zoneCoefInput.style.display = 'none';

    // Set up the confirm button
    confirmBtn.textContent = 'Confirmar';
    confirmBtn.className = 'smaller-button smaller-button-color-2';
    confirmBtn.style.display = 'none';

    // Insert the new elements into the form container
    const formContainer = box.querySelector('.form-container');
    formContainer.appendChild(instructionH4);
    formContainer.appendChild(zoneCoefInput);
    formContainer.appendChild(confirmBtn);

    uploadBtn.addEventListener('click', function() {
        pdfInput.click();
    });

    let textInput;

    pdfInput.addEventListener('change', function(event) {
      const file = event.target.files[0];

      if (file) {
          const formData = new FormData();
          formData.append('pdf', file);

          fetch('/validate-pdf', {
            method: 'POST',
            body: formData
          })
          .then(response => response.json())
          .then(data => {
              if (data.valid) {
                  // If valid, proceed with the upload
                  return fetch('/zone-confirm', {
                    method: 'POST',
                    body: formData
                  });
              } else {
                  // If invalid, render the error template
                  window.location.href = '/invalid-pdf';
              }
          })
          .then(response => {
              if (response) return response.json();
          })
          .then(data => {
              if (data) {
                  const zoneCoef = data.Cl;
                  textInput = data.text;
                  zoneCoefInput.value = zoneCoef;
                  zoneCoefInput.style.display = 'block';
                  confirmBtn.style.display = 'block';
                  instructionH4.style.display = 'block';
                  box.classList.add('expanded');
              }
          })
          .catch(error => {
              console.error('Error:', error);
          });
      }
    });

    // Add event listener for confirm button
    confirmBtn.addEventListener('click', function() {
      const zoneCoef = zoneCoefInput.value;

      // Use the hidden form at the end of index.html
      document.getElementById('zoneCoefInput').value = zoneCoef;
      document.getElementById('textInputHidden').value = textInput;
      document.getElementById('uploadForm').submit();
    });
  }
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

  if (window.location.pathname === '/index' || window.location.pathname === '/index.html' || window.location.pathname === '/') {

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
  }
});
