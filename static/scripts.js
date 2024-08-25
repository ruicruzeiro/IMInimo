
function showPopup(popupId) {
  var popup = document.getElementById(popupId);
  if (popup.style.display === "block") {
      popup.style.display = "none";
  } else {
      // Hide any other open popups
      var popups = document.querySelectorAll('.popup');
      popups.forEach(function(p) {
          p.style.display = 'none';
      });

      popup.style.display = "block";
  }
}

// Optional: Close the popup when clicking outside of it
document.addEventListener('click', function(event) {
  var isClickInsidePopup = event.target.closest('.popup');
  var isClickOnIcon = event.target.classList.contains('help-icon');

  if (!isClickInsidePopup && !isClickOnIcon) {
      var popups = document.querySelectorAll('.popup');
      popups.forEach(function(popup) {
          popup.style.display = 'none';
      });
  }
});

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
