# FedGuard Authentication

## Current State: Local JWT
FedGuard currently utilizes a local **JWT (JSON Web Token)** authentication strategy.
- Passwords are securely hashed using crypt (via passlib).
- The FastAPI backend validates credentials and issues an Access Token containing the user's sub (id) and 
ole.

## Future State: AWS Cognito
An abstract AuthProvider interface is implemented in the backend (pp.services.auth_provider). Currently it is bound to LocalJwtAuthProvider. In Phase 13/14, a CognitoAuthProvider will be integrated, shifting identity management directly to AWS while keeping the application code identical.

## Local Seed Users
For development, use the following credentials (password: password123):
- dmin@fedguard.dev
- 
esearcher@fedguard.dev
- iewer@fedguard.dev
