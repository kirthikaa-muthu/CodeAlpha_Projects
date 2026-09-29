\# Secure Coding Review – Student Management System



A Flask-based Student Management System developed as part of the CodeAlpha projects. The project was reviewed for common web application security issues and then remediated using secure coding practices.



\## Technologies



\- Python

\- Flask

\- SQLite

\- Flask-WTF

\- Werkzeug Security

\- HTML/CSS

\- Jinja2



\## Features



\- User authentication

\- Role-based access control

\- Student management

\- Add, edit and delete students

\- Module and teacher management

\- Student search

\- SQLite database

\- CSRF protection

\- Server-side input validation



\## Security Review and Remediation



The application was reviewed for several security weaknesses:



\- Hardcoded administrator credentials

\- Hardcoded Flask secret key

\- Debug mode enabled

\- Missing CSRF protection

\- Insufficient server-side input validation

\- Weak authorization controls



The identified issues were remediated using:



\- Database-backed authentication

\- Werkzeug password hashing

\- Environment-based secret configuration

\- Flask-WTF CSRF protection

\- Server-side validation

\- Role-based authorization

\- Parameterized SQL queries



\## Project Structure



```text

Secure-Coding-Review/

├── app.py

├── database/

│   └── database.py

├── security\_review/

│   └── security\_findings.md

├── static/

├── templates/

├── requirements.txt

└── README.md