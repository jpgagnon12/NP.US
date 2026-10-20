document.querySelector('#estimate-form').addEventListener('submit', (event) => {
  event.preventDefault();
  const fields = new FormData(event.currentTarget);
  const body = `Name: ${fields.get('name')}\nPhone: ${fields.get('phone')}\nEmail: ${fields.get('email')}\nService: ${fields.get('service')}\n\n${fields.get('message')}`;
  const href = `mailto:roofingperfectoinc@gmail.com?subject=${encodeURIComponent('Roofing estimate request')}&body=${encodeURIComponent(body)}`;
  window.location.href = href;
  document.querySelector('#form-status').textContent = 'Your email app can open the draft. You can also call 619-536-7332.';
});
