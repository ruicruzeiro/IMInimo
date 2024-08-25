document.addEventListener("DOMContentLoaded", function() {
  const boxes = document.querySelectorAll('.box');

  boxes.forEach(box => {
      box.addEventListener('click', function() {
          // Collapse all other boxes
          boxes.forEach(b => {
              if (b !== box) {
                  b.classList.remove('expanded');
              }
          });

          // Expand the clicked box
          box.classList.toggle('expanded');
      });
  });
});
