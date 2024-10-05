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
  const questionMarks = document.querySelectorAll('.question-mark'); // All question mark icons
  let currentHelpText = null; // To keep track of currently visible help text

  // Loop through each question mark
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
