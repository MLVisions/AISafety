// Note: navigation across pages is handled by simple anchor links in the HTML.
// This script focuses on tab switching within a page.

 // Handle tab switching within content sections
 document.querySelectorAll('.tab-container').forEach(container => {
   const buttons = container.querySelectorAll('.tab-button');
   buttons.forEach(btn => {
     btn.addEventListener('click', () => {
       // Remove active state from all buttons in this container
       buttons.forEach(b => b.classList.remove('active'));
       btn.classList.add('active');
       const section = btn.closest('.content-section');
       const allTabs = section.querySelectorAll('.tab-content');
       // Hide all tab content
       allTabs.forEach(tab => tab.classList.add('hidden'));
       // Show the selected tab content
       const tabId = btn.getAttribute('data-tab');
       const content = section.querySelector('#' + tabId);
       if (content) {
         content.classList.remove('hidden');
       }
     });
   });
 });

 // Default behaviour: show first content section or none
 // We can default to hiding all sections to prompt the user to choose a topic.
// When the page loads, hide all tab contents except the first in each container.
window.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.tab-container').forEach(container => {
    const buttons = container.querySelectorAll('.tab-button');
    const section = container.closest('.content-section');
    const allTabs = section.querySelectorAll('.tab-content');
    // Hide all tab contents
    allTabs.forEach(tab => tab.classList.add('hidden'));
    // Activate the first tab
    if (buttons.length > 0) {
      buttons[0].classList.add('active');
      const firstTabId = buttons[0].getAttribute('data-tab');
      const firstContent = section.querySelector('#' + firstTabId);
      if (firstContent) {
        firstContent.classList.remove('hidden');
      }
    }
  });
});