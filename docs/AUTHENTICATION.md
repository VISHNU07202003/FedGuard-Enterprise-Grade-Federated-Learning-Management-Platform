# FedGuard Authentication

## Current State: Local JWT
FedGuard currently utilizes a local **JWT (JSON Web Token)** authentication strategy.
- Passwords are securely hashed using bcrypt (via passlib).
- The FastAPI backend validates credentials and issues an Access Token containing the user's sub (id) and role.

## Future State: AWS Cognito
An abstract AuthProvider interface is implemented in the backend (app.services.auth_provider). Currently it is bound to LocalJwtAuthProvider. In Phase 13/14, a CognitoAuthProvider will be integrated, shifting identity management directly to AWS while keeping the application code identical.

## Local Seed Users
For development, use the seed script (backend/scripts/seed_users.py) to generate users. Do not hardcode or publish credentials in documentation.
