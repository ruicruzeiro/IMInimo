function showPopup() {
  const middleBox = document.querySelectorAll('.box')[1]; // Index 1 for the middle box
  const popup = document.getElementById('popup'); // Ensure popup is correctly defined

  // Get the bounding rectangle of the middle box
  const middleBoxRect = middleBox.getBoundingClientRect();

  // Get the bounding rectangle of the popup to calculate its dimensions
  const popupRect = popup.getBoundingClientRect();

  // Calculate the center position of the middle box
  const middleBoxCenterX = middleBoxRect.left + middleBoxRect.width / 2;

  // Calculate the left position for the popup to be centered horizontally
  const popupLeftX = middleBoxCenterX - (popupRect.width / 2);

  // Set the top position to be just below the middle box
  const popupTopY = middleBoxRect.bottom + window.scrollY + 10; // Adjust 10px for spacing

  // Apply calculated positions to the popup
  popup.style.top = `${popupTopY}px`;
  popup.style.left = `${popupLeftX + window.scrollX}px`;
  popup.style.display = 'block';
}
