/**
 * Client-side validation and confirmation feedback for the /contact form.
 * Falls back to native mailto: submission when JS is unavailable.
 */

const form = document.getElementById('contact-form');
const statusEl = document.getElementById('contact-form-status');

if (form instanceof HTMLFormElement && statusEl) {
  const fields = [
    {
      input: document.getElementById('contact-name'),
      error: document.getElementById('contact-name-error'),
      validate: (value) => (value.trim().length > 0 ? '' : 'Please enter your name.'),
    },
    {
      input: document.getElementById('contact-email'),
      error: document.getElementById('contact-email-error'),
      validate: (value) => {
        const trimmed = value.trim();
        if (!trimmed) return 'Please enter your email.';
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmed)
          ? ''
          : 'Please enter a valid email address.';
      },
    },
    {
      input: document.getElementById('contact-message'),
      error: document.getElementById('contact-message-error'),
      validate: (value) => (value.trim().length > 0 ? '' : 'Please enter a message.'),
    },
  ];

  const validateField = ({ input, error, validate }) => {
    if (!(input instanceof HTMLInputElement || input instanceof HTMLTextAreaElement) || !error) {
      return true;
    }
    const message = validate(input.value);
    error.textContent = message;
    if (message) {
      input.setAttribute('aria-invalid', 'true');
      return false;
    }
    input.removeAttribute('aria-invalid');
    return true;
  };

  for (const field of fields) {
    field.input?.addEventListener('input', () => {
      if (field.input?.getAttribute('aria-invalid') === 'true') {
        validateField(field);
      }
    });
  }

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    statusEl.textContent = '';

    let firstInvalid = null;
    for (const field of fields) {
      const valid = validateField(field);
      if (!valid && !firstInvalid && field.input instanceof HTMLElement) {
        firstInvalid = field.input;
      }
    }

    if (firstInvalid) {
      firstInvalid.focus();
      statusEl.textContent = 'Please fix the highlighted fields.';
      return;
    }

    form.reset();
    statusEl.textContent = 'Message ready — thanks for reaching out.';
  });
}
