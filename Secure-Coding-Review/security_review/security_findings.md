# Secure Coding Review

## Baseline

The application was functionally tested before security remediation.

A separate baseline copy of the working application has been preserved so that security changes can be compared against the original implementation.

---

# Security Findings

## Finding 1 — Hardcoded Administrator Credentials

### Description

The application contained administrator credentials directly in the Python source code.

### Evidence

The original login function compared the submitted username and password against hardcoded values.

### Risk

Anyone with access to the application source code may be able to obtain the administrator credentials.

This becomes particularly risky if the source code is stored in a public or shared Git repository.

### Security Impact

- Credential exposure
- Unauthorized access
- Difficult credential management
- Credentials cannot be changed without modifying source code

### Recommended Remediation

Administrator credentials should not be stored directly in application source code.

A secure implementation should use:

- Password hashing
- A database-backed user account
- Secure credential management
- Environment variables where appropriate

### Remediation

The hardcoded administrator credentials were removed from the login logic.

A `users` table was introduced to store user accounts, and passwords are stored using Werkzeug password hashing.

The login process now:

1. Retrieves the user from the database using a parameterized query.
2. Retrieves the stored password hash.
3. Verifies the submitted password using `check_password_hash()`.
4. Creates the authenticated session only after successful verification.
5. Clears any existing session when authentication fails.

### Verification

- Correct credentials successfully authenticate.
- Incorrect credentials are rejected.
- An unauthenticated user cannot access the dashboard.
- The plaintext administrator password is no longer compared directly in the login code.

### Status

**Remediated and verified.**

---

## Finding 2 — Hardcoded Flask Secret Key

### Description

The Flask application's secret key was directly embedded in the source code.

### Evidence

The original application defined the Flask secret key directly in `app.py`.

### Risk

If the secret key is exposed, the security of Flask's session mechanism may be compromised.

### Security Impact

- Session security weakness
- Potential session manipulation
- Secret exposure through source-code repositories

### Recommended Remediation

The secret key should be stored outside the application source code, preferably using an environment variable or another secure secret-management mechanism.

### Remediation

The Flask secret key was removed from the application source code.

The secret is now stored in an environment variable loaded from a `.env` file using `python-dotenv`.

The `.env` file is excluded from version control using `.gitignore`.

### Verification

- The application starts successfully.
- Login works correctly.
- Logout works correctly.
- Flask sessions continue to function.
- The secret key is no longer hardcoded in `app.py`.

### Status

**Remediated and verified.**

---

## Finding 3 — Debug Mode Enabled

### Description

The Flask application was configured with debugging enabled.

### Evidence

The original application started Flask with debug mode enabled.

### Risk

Debugging features can expose detailed application information and should not be enabled in a production environment.

### Security Impact

- Information disclosure
- Detailed error messages
- Exposure of internal application details

### Recommended Remediation

Disable debug mode for production deployment.

### Remediation

Debug mode was removed from the application as a hardcoded setting.

The application now reads the debug configuration from the `FLASK_DEBUG` environment variable.

The default value is `False`, ensuring that debugging is disabled unless explicitly enabled during development.

### Verification

- The application starts successfully.
- The Flask debugger is no longer active by default.
- The application continues to support login and normal functionality.
- The application displayed `Debug mode: off` when started.

### Status

**Remediated and verified.**

---

## Finding 4 — Missing CSRF Protection

### Description

The application contained state-changing POST requests but did not previously implement CSRF protection.

### Affected Operations

- Login
- Add Student
- Edit Student
- Delete Student

### Risk

An attacker could potentially construct a malicious webpage that causes an authenticated user's browser to submit an unwanted request to the application.

### Security Impact

- Unauthorized state-changing requests
- Unwanted modification of student records
- Unwanted deletion of student records

### Recommended Remediation

Implement CSRF protection for state-changing forms using a mechanism such as Flask-WTF CSRF protection.

### Remediation

Flask-WTF `CSRFProtect` was enabled in the application.

CSRF tokens were added to the relevant forms:

- Login form
- Add Student form
- Edit Student form
- Delete Student form

State-changing requests are therefore required to contain a valid CSRF token.

### Verification

- Login form includes a CSRF token.
- Add Student form includes a CSRF token.
- Edit Student form includes a CSRF token.
- Delete Student form includes a CSRF token.
- Normal login, add, edit, and delete operations continue to work with CSRF protection enabled.

### Status

**Remediated and verified.**

---

## Finding 5 — Insufficient Server-Side Input Validation

### Description

Student information was previously accepted from HTTP requests with limited server-side validation.

### Affected Fields

- Student name
- Email
- Course / Module
- Year

### Risk

Client-side validation alone can be bypassed because users can send requests directly to the server.

### Security Impact

- Invalid data entering the database
- Unexpected application behaviour
- Poor data integrity

### Recommended Remediation

Validate submitted data on the server.

Validation should include appropriate:

- Length restrictions
- Email format validation
- Year validation
- Module validation
- Required-field validation

### Remediation

Server-side validation was added to the Add Student and Edit Student operations.

The validation checks:

- Student name is required.
- Student name length is restricted.
- Email address is required.
- Email format is validated.
- Course/module is required.
- Academic year must be a valid number.
- Academic year must be between 1 and 5.
- The selected module must exist in the database.

### Verification

The validation was tested using invalid input.

- Invalid email addresses were rejected.
- Invalid academic year values were rejected.
- Valid student information continues to be accepted.
- Existing modules are checked against the database before student records are created or updated.

### Status

**Remediated and verified.**

---

## Finding 6 — Weak Authorization Model

### Description

The original application checked whether a user was authenticated, but the role stored in the session was not used to enforce specific permissions.

### Evidence

The original application stored an administrator role in the session, but management routes primarily checked whether a username existed in the session.

### Risk

The application did not provide sufficient role separation for different user types.

### Security Impact

- Limited role separation
- Potential for excessive privileges as additional user types are introduced
- Difficult to enforce least-privilege access

### Recommended Remediation

Implement explicit authorization checks based on user roles and permissions.

For example:

- Administrator — full student management
- Teacher — appropriate student/module access
- Other users — restricted access

### Remediation

An `admin_required()` authorization helper was introduced.

The helper verifies:

1. The user is authenticated.
2. The user's session role is `admin`.

Administrative operations are now protected by this authorization check.

The following operations require administrator privileges:

- Add Student
- Edit Student
- Manage Edit
- Manage Delete
- Delete Student

Unauthenticated users are redirected to the login page, while authenticated non-admin users receive an HTTP 403 Access Denied response when attempting to access administrative operations.

### Verification

A separate non-admin test account was created with the role `user`.

The non-admin account was tested against the administrative functions.

Results:

- Viewing students — permitted.
- Viewing modules — permitted.
- Viewing teachers — permitted.
- Adding students — denied.
- Editing students — denied.
- Deleting students — denied.

The administrator account was also tested to confirm that authorized Add, Edit, and Delete operations continue to function.

### Status

**Remediated and verified.**

---

# Security Strengths Identified

## Parameterized SQL Queries

The application uses parameterized SQL queries for its current student search, insert, update, and delete operations.

This reduces the risk of SQL injection in the reviewed database operations.

### Status

No SQL injection vulnerability identified in the reviewed queries.