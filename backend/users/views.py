"""Django REST framework views for user management.

Provides REST API endpoints for comprehensive user account management
including user administration, profile management, and MFA operations
with proper authentication and authorization controls.
"""

from typing import Any

from django.core.exceptions import PermissionDenied
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import GenericViewSet

from framework.views import BaseViewSet
from platforms.email.notifications import SMTP
from security.authentication.jwt import CookieJWTAuthentication
from security.authorization.permissions import IsNotAuthenticated, RekonoModelPermission
from security.authorization.roles import Role
from users.filters import UserFilter
from users.models import User
from users.serializers import (
    CreateUserSerializer,
    DisableMfaSerializer,
    EnableMfaSerializer,
    InviteUserSerializer,
    ProfileSerializer,
    RegisterMfaSerializer,
    RequestPasswordResetSerializer,
    ResetPasswordSerializer,
    RestrictedUserSerializer,
    UpdatePasswordSerializer,
    UpdateRoleSerializer,
    UserSerializer,
    VerifyEmailSerializer,
)


class UserViewSet(BaseViewSet):
    """ViewSet for user account management operations.

    Provides REST API endpoints for user administration including invitation,
    role management, account enabling/disabling, and password reset operations.
    Restricted to admin users for security.

    Attributes:
        queryset (QuerySet): User model instances
        serializer_class (Serializer): Default serializer for User model
        filterset_class (FilterSet): Filter class for user queries
        permission_classes (list): Required permissions for access control
        search_fields (list): Fields available for text search
        ordering_fields (list): Fields available for result ordering
        http_method_names (list): Allowed HTTP methods
    """

    serializer_class = UserSerializer
    queryset = User.objects.all()
    filterset_class = UserFilter
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    search_fields = ["username", "first_name", "last_name", "email"]
    ordering_fields = ["id", "username", "first_name", "last_name", "email", "date_joined", "last_login"]
    http_method_names = ["get", "post", "put", "delete"]

    def get_serializer_class(self) -> type[Serializer]:
        """Get the serializer class based on the requesting user's role.

        Admins receive the full serializer including email addresses, which they
        legitimately need to manage users and project members. Any other role
        receives a restricted serializer that hides other users' emails to
        prevent phishing and social engineering.

        Returns:
            type[Serializer]: UserSerializer for admins, RestrictedUserSerializer otherwise
        """
        if self.request.user.is_authenticated and self.request.user.groups.filter(name=Role.ADMIN.value).exists():
            return UserSerializer
        return RestrictedUserSerializer

    def get_object_if_not_current_user(self, request: Request, pk: str) -> User:
        """Get user object ensuring it's not the current user.

        Prevents users from performing administrative actions on themselves.

        Args:
            request (Request): The HTTP request object
            pk (str): Primary key of the user

        Returns:
            User: The requested user object

        Raises:
            PermissionDenied: If user tries to modify their own account
        """
        instance = self.get_object()
        if instance.id == request.user.id:
            raise PermissionDenied()
        return instance

    @extend_schema(request=InviteUserSerializer, responses={201: UserSerializer})
    def create(self, request: Request, *args, **kwargs):
        """Create and invite new user account.

        Creates inactive user account with specified role and sends invitation
        email for account activation.

        Args:
            request (Request): HTTP request with user invitation data

        Returns:
            Response: HTTP 201 with created user data
        """
        serializer = InviteUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            self.get_serializer(instance=serializer.create(serializer.validated_data)).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(request=CreateUserSerializer, responses={201: UserSerializer})
    @action(detail=False, methods=["POST"], url_path="signup", permission_classes=[IsNotAuthenticated])
    def create_after_invitation(self, request: Request, *args, **kwargs) -> Response:
        """Complete user account creation after invitation.

        Activates user account after successful OTP verification from
        invitation email. Sets username, password, and personal information.

        Args:
            request (Request): HTTP request with account creation data

        Returns:
            Response: HTTP 201 with activated user data
        """
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            self.get_serializer(instance=serializer.create(serializer.validated_data)).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(request=None, responses={204: None})
    @action(detail=True, methods=["POST"])
    def resend(self, request: Request, pk: str) -> Response:
        """Resend invitation email to user.

        Sends new invitation email with fresh OTP to users who haven't
        completed account creation.

        Args:
            request (Request): The HTTP request object
            pk (str): Primary key of the user

        Returns:
            Response: HTTP 204 on success, HTTP 400 with error on failure
        """
        user = self.get_object()
        if user.is_active is not None or user.otp is None:
            return Response({"user": "User account has been already created"}, status=status.HTTP_400_BAD_REQUEST)
        if not SMTP().is_available():
            return Response(  # pragma: no cover
                {"smtp": "SMTP client is not available to send the invitation"}, status=status.HTTP_400_BAD_REQUEST
            )
        User.objects.send_invitation(user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(request=RequestPasswordResetSerializer, responses={200: None}, methods=["POST"])
    @extend_schema(request=ResetPasswordSerializer, responses={200: None}, methods=["PUT"])
    @action(detail=False, methods=["POST", "PUT"], url_path="reset-password", permission_classes=[IsNotAuthenticated])
    def reset_password(self, request: Request, *args, **kwargs) -> Response:
        """Handle password reset workflow.

        POST: Request password reset by sending OTP email
        PUT: Complete password reset with OTP verification and clear the
        authentication cookies so the client must sign in again with the new password

        Args:
            request (Request): HTTP request with reset data

        Returns:
            Response: HTTP 200 on successful operation
        """
        serializer_class = (
            RequestPasswordResetSerializer if request.method.lower() == "post" else ResetPasswordSerializer
        )
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = Response(status=status.HTTP_200_OK)
        if request.method.lower() == "put":
            CookieJWTAuthentication.clear_cookies(response)
        return response

    @extend_schema(request=VerifyEmailSerializer, responses={200: None})
    @action(detail=False, methods=["POST"], url_path="verify-email", permission_classes=[AllowAny])
    def verify_email(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Confirm a pending email address change.

        Verifies the OTP sent to the new address and applies the email change. Public
        endpoint because the verification link may be opened while the user is still
        logged in or from a different device.

        Args:
            request (Request): HTTP request with the OTP to verify

        Returns:
            Response: HTTP 200 on success, HTTP 401 if the OTP is invalid or expired
        """
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)

    @extend_schema(request=UpdateRoleSerializer, responses={200: UserSerializer})
    def update(self, request, pk: str, *args, **kwargs):
        """Update user role assignment.

        Updates the role assigned to a user account. Cannot be used on
        the current user's own account.

        Args:
            request (Request): HTTP request with role update data
            pk (str): Primary key of the user

        Returns:
            Response: HTTP 200 with updated user data
        """
        instance = self.get_object_if_not_current_user(request, pk)
        serializer = UpdateRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            self.get_serializer(instance=serializer.update(instance, serializer.validated_data)).data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request: Request, pk: str, *args: Any, **kwargs: Any) -> Response:
        """Delete or disable user account.

        Deletes invited users who haven't created accounts, or disables
        active users while preserving their data.

        Args:
            request (Request): The HTTP request object
            pk (str): Primary key of the user

        Returns:
            Response: HTTP 204 on successful operation
        """
        instance = self.get_object_if_not_current_user(request, pk)
        if instance.is_active is None:
            # User was invited but the account wasn't created
            super().destroy(request, *args, **kwargs)
        else:
            User.objects.disable_user(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(request=None, responses={200: UserSerializer})
    @action(detail=True, methods=["POST"])
    def enable(self, request: Request, pk: str) -> Response:
        """Enable disabled user account.

        Reactivates a disabled user account and sends notification email
        with new OTP for account access.

        Args:
            request (Request): The HTTP request object
            pk (str): Primary key of the user

        Returns:
            Response: HTTP 200 with enabled user data
        """
        instance = self.get_object_if_not_current_user(request, pk)
        User.objects.enable_user(instance)
        return Response(self.get_serializer(instance=instance).data, status=status.HTTP_200_OK)


class BaseProfileViewSet(GenericViewSet):
    """Base ViewSet for user profile management operations.

    Provides common functionality for profile-related ViewSets with
    simplified permission handling for authenticated users.

    Attributes:
        queryset (QuerySet): User model instances
        serializer_class (Serializer): Default serializer for profile operations
        permission_classes (list): Required permissions for access control
    """

    serializer_class = ProfileSerializer
    queryset = User.objects.all()
    # Only IsAuthenticated class is required because all users can manage their own profile
    permission_classes = [IsAuthenticated]

    def _get(self, request: Request) -> Response:
        """Get current user's profile data.

        Args:
            request (Request): The HTTP request object

        Returns:
            Response: HTTP 200 with user profile data
        """
        return Response(self.get_serializer(instance=request.user).data, status=status.HTTP_200_OK)

    def _update(self, request: Request, serializer_class: Serializer) -> Serializer:
        """Update user profile with specified serializer.

        Args:
            request (Request): HTTP request with profile update data
            serializer_class (Serializer): Serializer class to use for validation

        Returns:
            Serializer: Validated serializer instance
        """
        serializer = serializer_class(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(request.user, serializer.validated_data)
        return serializer


class ProfileViewSet(BaseProfileViewSet):
    """ViewSet for user profile management.

    Provides REST API endpoints for users to manage their own profile
    information and password with proper validation and security controls.
    """

    @action(detail=False, methods=["GET"])
    def get_profile(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Get current user's profile information.

        Args:
            request (Request): The HTTP request object

        Returns:
            Response: HTTP 200 with profile data
        """
        return self._get(request)

    @action(detail=False, methods=["PUT"])
    def update_profile(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Update current user's profile information.

        Args:
            request (Request): HTTP request with profile update data

        Returns:
            Response: HTTP 200 with updated profile data
        """
        serializer = self._update(request, self.serializer_class)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=UpdatePasswordSerializer, responses={200: None})
    @action(detail=False, methods=["PUT"])
    def update_password(self, request: Request) -> Response:
        """Update current user's password.

        Validates old password and updates to new password with security
        cleanup including token invalidation. Clears the authentication cookies
        on the response so the current session must re-authenticate.

        Args:
            request (Request): HTTP request with password change data

        Returns:
            Response: HTTP 200 on successful password update
        """
        self._update(request, UpdatePasswordSerializer)
        return CookieJWTAuthentication.clear_cookies(Response(status=status.HTTP_200_OK))


class MfaViewSet(BaseProfileViewSet):
    """ViewSet for Multi-Factor Authentication management.

    Provides REST API endpoints for MFA registration, enabling, and disabling
    operations with TOTP authenticator app integration.

    Attributes:
        authentication_classes (list): JWT authentication required for MFA operations
    """

    authentication_classes = [CookieJWTAuthentication]

    @extend_schema(request=None, responses={200: RegisterMfaSerializer})
    @action(detail=False, methods=["POST"])
    def register(self, request: Request, *args, **kwargs) -> Response:
        """Register MFA for current user.

        Generates MFA secret and returns QR code provisioning URL for
        authenticator app setup.

        Args:
            request (Request): The HTTP request object

        Returns:
            Response: HTTP 200 with QR code URL, HTTP 400 if MFA already enabled
        """
        if request.user.mfa:
            return Response({"mfa": "MFA is already enabled"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            RegisterMfaSerializer({"url": User.objects.register_mfa(request.user)}, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=EnableMfaSerializer, responses={200: ProfileSerializer})
    @action(detail=False, methods=["POST"])
    def enable(self, request: Request) -> Response:
        """Enable MFA for current user.

        Enables MFA after verifying OTP from authenticator app.
        Requires prior MFA registration.

        Args:
            request (Request): HTTP request with MFA verification data

        Returns:
            Response: HTTP 200 with updated profile, HTTP 400 on validation error
        """
        if request.user.mfa:
            return Response({"mfa": "MFA is already enabled"}, status=status.HTTP_400_BAD_REQUEST)
        if not request.user.secret:
            return Response({"mfa": "MFA is not registered yet"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = EnableMfaSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self._get(request)

    @extend_schema(request=DisableMfaSerializer, responses={200: ProfileSerializer})
    @action(detail=False, methods=["POST"])
    def disable(self, request: Request) -> Response:
        """Disable MFA for current user.

        Disables MFA after verifying current password or OTP.
        Removes MFA requirement for future logins.

        Args:
            request (Request): HTTP request with MFA disable verification

        Returns:
            Response: HTTP 200 with updated profile, HTTP 400 on validation error
        """
        if not request.user.mfa:
            return Response({"mfa": "MFA is already disabled"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = DisableMfaSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self._get(request)
