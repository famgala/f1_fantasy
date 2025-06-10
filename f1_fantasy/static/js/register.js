/**
 * Registration form validation module
 * Handles password validation, password matching, and form submission
 */
class RegistrationForm {
    constructor() {
        // Wait for DOM to be fully loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initialize());
        } else {
            this.initialize();
        }
    }

    initialize() {
        console.log('Initializing registration form...');
        
        // Get form elements
        this.form = document.getElementById('registerForm');
        this.password = document.getElementById('register_password');
        this.passwordConfirm = document.getElementById('register_password_confirm');
        this.submitButton = document.getElementById('register_submit');
        this.passwordMatchFeedback = document.getElementById('passwordMatchFeedback');
        
        // Password requirement elements
        this.requirements = {
            length: document.getElementById('length'),
            uppercase: document.getElementById('uppercase'),
            lowercase: document.getElementById('lowercase'),
            number: document.getElementById('number'),
            special: document.getElementById('special'),
            match: document.getElementById('match')
        };
        
        // Password toggle buttons
        this.togglePassword = document.getElementById('togglePassword');
        this.togglePasswordConfirm = document.getElementById('togglePasswordConfirm');
        
        // Verify all elements are found
        const missingElements = [];
        if (!this.form) missingElements.push('form');
        if (!this.password) missingElements.push('password');
        if (!this.passwordConfirm) missingElements.push('passwordConfirm');
        if (!this.submitButton) missingElements.push('submitButton');
        if (!this.passwordMatchFeedback) missingElements.push('passwordMatchFeedback');
        
        Object.entries(this.requirements).forEach(([key, element]) => {
            if (!element) missingElements.push(`requirement-${key}`);
        });
        
        if (!this.togglePassword) missingElements.push('togglePassword');
        if (!this.togglePasswordConfirm) missingElements.push('togglePasswordConfirm');
        
        if (missingElements.length > 0) {
            console.error('Missing required elements:', missingElements);
            return;
        }
        
        console.log('All form elements found successfully');
        
        // Add event listeners
        this.password.addEventListener('input', () => {
            console.log('Password input event triggered');
            this.validatePassword();
        });
        
        this.passwordConfirm.addEventListener('input', () => {
            console.log('Password confirm input event triggered');
            this.validatePassword();
        });
        
        this.togglePassword.addEventListener('click', () => {
            console.log('Toggle password visibility');
            this.togglePasswordVisibility(this.password, this.togglePassword);
        });
        
        this.togglePasswordConfirm.addEventListener('click', () => {
            console.log('Toggle password confirm visibility');
            this.togglePasswordVisibility(this.passwordConfirm, this.togglePasswordConfirm);
        });
        
        // Initial validation
        console.log('Performing initial validation');
        this.validatePassword();
        
        // Auto-focus email field
        const emailField = document.getElementById('register_email');
        if (emailField && !emailField.value) {
            emailField.focus();
        }
        
        console.log('Registration form initialization complete');
    }
    
    validatePassword() {
        const password = this.password.value;
        const confirmPassword = this.passwordConfirm.value;
        
        // Password requirements
        const hasLength = password.length >= 8;
        const hasUppercase = /[A-Z]/.test(password);
        const hasLowercase = /[a-z]/.test(password);
        const hasNumber = /[0-9]/.test(password);
        const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(password);
        const passwordsMatch = password === confirmPassword && password !== '';
        
        console.log('Password validation results:', {
            hasLength,
            hasUppercase,
            hasLowercase,
            hasNumber,
            hasSpecial,
            passwordsMatch
        });
        
        // Update requirement states
        this.updateRequirement('length', hasLength);
        this.updateRequirement('uppercase', hasUppercase);
        this.updateRequirement('lowercase', hasLowercase);
        this.updateRequirement('number', hasNumber);
        this.updateRequirement('special', hasSpecial);
        this.updateRequirement('match', passwordsMatch);
        
        // Update password match feedback
        if (confirmPassword) {
            if (passwordsMatch) {
                this.passwordMatchFeedback.textContent = 'Passwords match';
                this.passwordMatchFeedback.className = 'password-match-feedback valid';
            } else {
                this.passwordMatchFeedback.textContent = 'Passwords do not match';
                this.passwordMatchFeedback.className = 'password-match-feedback invalid';
            }
        } else {
            this.passwordMatchFeedback.textContent = '';
        }
        
        // Enable/disable submit button
        const allValid = hasLength && hasUppercase && hasLowercase && hasNumber && hasSpecial && passwordsMatch;
        this.submitButton.disabled = !allValid;
        console.log('Submit button state:', { disabled: !allValid });
    }
    
    updateRequirement(id, isValid) {
        const requirement = this.requirements[id];
        if (!requirement) {
            console.warn(`Requirement element not found: ${id}`);
            return;
        }
        
        // Update the requirement's class
        requirement.className = isValid ? 'valid' : 'invalid';
        
        // Update the icon
        const icon = requirement.querySelector('i');
        if (icon) {
            icon.className = isValid ? 'fas fa-check-circle' : 'fas fa-times-circle';
        } else {
            console.warn(`Icon not found for requirement: ${id}`);
        }
        
        console.log(`Updated requirement ${id}:`, { isValid });
    }
    
    togglePasswordVisibility(input, button) {
        if (!input || !button) {
            console.error('Invalid input or button element');
            return;
        }
        
        const type = input.type === 'password' ? 'text' : 'password';
        input.type = type;
        
        const icon = button.querySelector('i');
        if (icon) {
            icon.className = type === 'password' ? 'fas fa-eye' : 'fas fa-eye-slash';
        }
        
        button.setAttribute('aria-label', type === 'password' ? 'Show password' : 'Hide password');
    }
}

// Initialize the registration form
try {
    console.log('Creating registration form instance...');
    new RegistrationForm();
} catch (error) {
    console.error('Failed to initialize registration form:', error);
} 