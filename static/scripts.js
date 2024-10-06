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
