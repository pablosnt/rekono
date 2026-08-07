"""Authentication of the Rekono API.

Supports two credentials, the JWT tokens that the frontend obtains from the login
endpoints and keeps in cookies, and the API tokens used by the external clients.
The login can also require a second factor, based on TOTP with an email one-time
password fallback.
"""
