document.addEventListener('DOMContentLoaded', () => {

    // Animated Placeholders Logic - Handling auto-fill
    const inputs = document.querySelectorAll('.form-control');
    inputs.forEach(input => {
        // Check initial state
        if (input.value) {
            input.classList.add('has-value');
        }

        input.addEventListener('input', () => {
            if (input.value) {
                input.classList.add('has-value');
            } else {
                input.classList.remove('has-value');
            }
        });

        // Ensure browser autofill triggers label move
        input.addEventListener('animationstart', (e) => {
            if (e.animationName === "onAutoFillStart") {
                input.classList.add('has-value');
            }
        });
    });

    // We can add a simple particle effect or enhance the 'glitch' effect here later if needed.
    // For now, the CSS handles most visual interactions.

    // Form submission handling if needed for AJAX/Fetch as requested
    // Since Django auth forms are robust, we'll hook into submit but respect default if action is set,
    // or hijack if we want full SPA feel. 
    // The user requested: "Javascript fetch() use karke data ko ... bhejein"
    // So we will intercept the register form.

    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = new FormData(registerForm);
            const errorContainer = document.getElementById('form-errors');
            errorContainer.innerHTML = ''; // Clear previous errors

            // Show loading state on button
            const btn = registerForm.querySelector('button[type="submit"]');
            const originalBtnText = btn.innerText;
            btn.innerText = 'Processing...';
            btn.disabled = true;

            try {
                // Determine valid URL - if action is set, use it, else default
                const url = registerForm.action;

                const response = await fetch(url, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                // If the response is a redirect (success), window.location will handle it if standard submit,
                // but with fetch, we need to check redirected status or JSON response.
                // NOTE: Django standard views return HTML by default unless configured for JSON.
                // Assuming standard Django view returns a redirect on success, or re-renders form with errors.
                // To support 'fetch' fully with JSON errors, the view needs to return JSON.
                // However, user asked to "connect... via fetch".
                // If the view returns HTML (whole page), parsing it in JS is messy.
                // A better approach for "visual feedback" without changing backend views to DRF/JSON yet
                // is to just let the form submit normally, OR parse the returned HTML for errors.

                // Let's assume for this specific request, we want to see if we get a redirect or HTML content.
                if (response.redirected) {
                    window.location.href = response.url;
                } else {
                    const html = await response.text();
                    // If we get HTML back, it likely means errors or success message on same page.
                    // We can replace the document body or specific part.
                    // But to be "techy" and smooth, we want to extract errors.

                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');

                    // Check if there are error lists in the returned HTML
                    // Django forms usually render <ul class="errorlist">
                    const newErrors = doc.querySelectorAll('.errorlist');
                    const newAlerts = doc.querySelectorAll('.alert-box'); // If backend renders messages

                    if (newErrors.length > 0 || newAlerts.length > 0) {
                        // Extract and display errors smoothly
                        // Re-render only the form part or show a global alert

                        // Simple strategy: Replace the form content with the new form content (with errors)
                        // This keeps the page fresh without full reload
                        const newForm = doc.getElementById('register-form');
                        if (newForm) {
                            registerForm.innerHTML = newForm.innerHTML;
                            // Re-attach listeners? Yes. A full reload is safer for standard Django views, 
                            // but we can simulate SPA. 
                            // Ideally, we'd just use standard submit for reliability unless an API endpoint returning JSON exists.
                            // USER said: "Backend se aane wale validation errors... ko frontend par neon red alert boxes mein dikhayein"

                            // Creating custom alert boxes from the error list
                            const errorMsgs = [];
                            newErrors.forEach(ul => {
                                ul.querySelectorAll('li').forEach(li => errorMsgs.push(li.innerText));
                            });

                            if (errorMsgs.length > 0) {
                                const errorHtml = errorMsgs.map(msg =>
                                    `<div class="alert-box alert-error">
                                         <i class="fas fa-exclamation-triangle"></i>
                                         <span>${msg}</span>
                                     </div>`
                                ).join('');
                                errorContainer.innerHTML = errorHtml;
                            }
                        }
                    } else {
                        // If no errors found but no redirect, maybe just replace the body (e.g. success message)
                        document.body.innerHTML = doc.body.innerHTML;
                    }
                }

            } catch (error) {
                console.error('Error:', error);
                errorContainer.innerHTML = `<div class="alert-box alert-error">
                                                <i class="fas fa-exclamation-triangle"></i>
                                                <span>An unexpected connection error occurred.</span>
                                            </div>`;
            } finally {
                btn.innerText = originalBtnText;
                btn.disabled = false;
            }
        });
    }

});
