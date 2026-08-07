"""Endpoints to administrate the users and to manage the profile of each one."""

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
    """Administrate the users: invitations, roles, and account status.

    It also holds the endpoints of the operations that anonymous users perform over
    their own account, like the registration and the password reset.

    Attributes:
        serializer_class: Serializer used for the administrators, replaced by
          get_serializer_class for the rest of the roles.
        queryset: All the users, since they aren't scoped to any project.
        filterset_class: Filters available to search users.
        permission_classes: Role permissions, which only let the administrators
          manage the accounts.
        search_fields: Fields used by the text search.
        ordering_fields: Fields that can be used to order the results.
        http_method_names: Standard CRUD methods, where PUT changes the role and
          DELETE disables the account.
    """

    serializer_class = UserSerializer
    queryset = User.objects.all()
    filterset_class = UserFilter
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    search_fields = ["username", "first_name", "last_name", "email"]
    ordering_fields = ["id", "username", "first_name", "last_name", "email", "date_joined", "last_login"]
    http_method_names = ["get", "post", "put", "delete"]

    def get_serializer_class(self) -> type[Serializer]:
        """Get the serializer that the role of the user is allowed to read.

        Admins receive the full serializer including email addresses, which they
        legitimately need to manage users and project members. Any other role
        receives a restricted serializer that hides other users' emails to
        prevent phishing and social engineering.

        Returns:
            The serializer that the role of the requester is allowed to read.
        """
        if self.request.user.is_authenticated and self.request.user.groups.filter(name=Role.ADMIN.value).exists():
            return UserSerializer
        return RestrictedUserSerializer

    def get_object_if_not_current_user(self, request: Request, pk: str) -> User:
        """Get the user of the request path, as long as it isn't the requester.

        Args:
            request: Request whose user must be a different one.
            pk: Identifier of the user, taken from the URL and already resolved by
              the viewset, so it isn't read here.

        Returns:
            The user of the path.

        Raises:
            PermissionDenied: If administrators try to change their own role or
              disable their own account, which would leave them locked out.
        """
        instance = self.get_object()
        if instance.id == request.user.id:
            raise PermissionDenied()
        return instance

    @extend_schema(request=InviteUserSerializer, responses={201: UserSerializer})
    def create(self, request: Request, *args, **kwargs):
        """Invite a new user, creating their account in the invited state.

        Args:
            request: Request with the email address and the role of the invitation.
            *args: Standard view arguments.
            **kwargs: Standard view arguments.

        Returns:
            A 201 response with the invited user.
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
        """Complete the registration of an invited user with their invitation OTP.

        Args:
            request: Request with the account details and the invitation OTP.
            *args: Standard view arguments.
            **kwargs: Standard view arguments.

        Returns:
            A 201 response with the registered user, who can now log in.
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
        """Send the invitation email again, with a new one-time password.

        Args:
            request: Request that asks for the invitation to be sent again.
            pk: Identifier of the invited user, taken from the URL.

        Returns:
            An empty response, or a validation error if the account was already
            created or the invitation can't be sent because SMTP isn't available.
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
        """Request a password reset with POST, and apply it with PUT.

        The authentication cookies are cleared once the password is changed, so the
        client has to log in again with the new one.

        Args:
            request: Request with the email address for POST, or the one-time
              password and the new password for PUT.
            *args: Standard view arguments.
            **kwargs: Standard view arguments.

        Returns:
            An empty 200 response in both cases, so the answer to a request never
            reveals whether the email address belongs to a Rekono user.
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
        """Confirm a pending email address change with the OTP sent to it.

        Anyone can call it, since the verification link may be opened while the user
        is still logged in or from a different device.

        Args:
            request: Request with the one-time password sent to the new address.
            *args: Standard view arguments.
            **kwargs: Standard view arguments.

        Returns:
            An empty 200 response.
        """
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)

    @extend_schema(request=UpdateRoleSerializer, responses={200: UserSerializer})
    def update(self, request, pk: str, *args, **kwargs):
        """Change the role of a user, which is the only thing that can be updated.

        Args:
            request: Request with the new role.
            pk: Identifier of the user, taken from the URL.
            *args: Standard view arguments.
            **kwargs: Standard view arguments.

        Returns:
            A 200 response with the updated user.
        """
        instance = self.get_object_if_not_current_user(request, pk)
        serializer = UpdateRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            self.get_serializer(instance=serializer.update(instance, serializer.validated_data)).data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request: Request, pk: str, *args: Any, **kwargs: Any) -> Response:
        """Disable a user, or delete it if its account was never created.

        A user that already worked in Rekono is disabled instead of deleted, so the
        tasks, findings, and notes that reference them are kept.

        Args:
            request: Request that asks for the user to be removed.
            pk: Identifier of the user, taken from the URL.
            *args: Standard view arguments.
            **kwargs: Standard view arguments.

        Returns:
            An empty 204 response, whether the account was disabled or deleted.
        """
        instance = self.get_object_if_not_current_user(request, pk)
        if instance.is_active is None:
            super().destroy(request, *args, **kwargs)
        else:
            User.objects.disable_user(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(request=None, responses={200: UserSerializer})
    @action(detail=True, methods=["POST"])
    def enable(self, request: Request, pk: str) -> Response:
        """Enable a disabled user, sending them an email to set a new password.

        Args:
            request: Request that asks for the account to be enabled.
            pk: Identifier of the user, taken from the URL.

        Returns:
            A 200 response with the enabled user.
        """
        instance = self.get_object_if_not_current_user(request, pk)
        User.objects.enable_user(instance)
        return Response(self.get_serializer(instance=instance).data, status=status.HTTP_200_OK)


class BaseProfileViewSet(GenericViewSet):
    """Base viewset of the endpoints where a user manages their own account.

    Attributes:
        serializer_class: Serializer of the profile of the user.
        queryset: All the users, although only the requester is ever accessed.
        permission_classes: Only authentication is required, because all users can
          manage their own profile.
    """

    serializer_class = ProfileSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def _get(self, request: Request) -> Response:
        """Build the response with the profile of the user that performs the request.

        Args:
            request: Request whose user is the one being serialized.

        Returns:
            A 200 response with their profile.
        """
        return Response(self.get_serializer(instance=request.user).data, status=status.HTTP_200_OK)

    def _update(self, request: Request, serializer_class: Serializer) -> Serializer:
        """Update the user that performs the request with the given serializer.

        Args:
            request: Request whose user is updated with its own body.
            serializer_class: Serializer that validates and applies the change.

        Returns:
            The serializer, already validated and applied, so the caller can build
            the response with its data.
        """
        serializer = serializer_class(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(request.user, serializer.validated_data)
        return serializer


class ProfileViewSet(BaseProfileViewSet):
    """Read and update the profile and the password of the user that requests it."""

    @action(detail=False, methods=["GET"])
    def get_profile(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Get the profile of the user that performs the request.

        Args:
            request: Request whose user is the one being read.
            *args: Standard view arguments.
            **kwargs: Standard view arguments.

        Returns:
            A 200 response with their profile.
        """
        return self._get(request)

    @action(detail=False, methods=["PUT"])
    def update_profile(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Update the profile of the user that performs the request.

        Args:
            request: Request with the profile fields to update.
            *args: Standard view arguments.
            **kwargs: Standard view arguments.

        Returns:
            A 200 response with the updated profile.
        """
        serializer = self._update(request, self.serializer_class)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=UpdatePasswordSerializer, responses={200: None})
    @action(detail=False, methods=["PUT"])
    def update_password(self, request: Request) -> Response:
        """Change the password of the user that performs the request.

        The authentication cookies are cleared, since changing the password closes
        all the sessions of the user, including the current one.

        Args:
            request: Request with the current and the new passwords.

        Returns:
            An empty 200 response, with the authentication cookies removed.
        """
        self._update(request, UpdatePasswordSerializer)
        return CookieJWTAuthentication.clear_cookies(Response(status=status.HTTP_200_OK))


class MfaViewSet(BaseProfileViewSet):
    """Register, enable, and disable the MFA of the user that requests it.

    Attributes:
        authentication_classes: Only the JWT authentication, so the MFA can't be
          managed by a client authenticated with an API token.
    """

    authentication_classes = [CookieJWTAuthentication]

    @extend_schema(request=None, responses={200: RegisterMfaSerializer})
    @action(detail=False, methods=["POST"])
    def register(self, request: Request, *args, **kwargs) -> Response:
        """Generate the TOTP secret and return the URI for the authenticator app.

        Args:
            request: Request whose user is registering their second factor.
            *args: Standard view arguments.
            **kwargs: Standard view arguments.

        Returns:
            The provisioning URI, or a validation error if the user already has MFA
            enabled, since a new secret would invalidate their current one.
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
        """Enable the MFA of the user, verifying a code from their authenticator app.

        Args:
            request: Request with the code generated by the authenticator app.

        Returns:
            The updated profile, or a validation error if the MFA is already enabled
            or the TOTP secret hasn't been registered yet.
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
        """Disable the MFA of the user, verifying a code before doing it.

        Args:
            request: Request with the MFA code that proves the account ownership.

        Returns:
            The updated profile, or a validation error if the MFA is already
            disabled.
        """
        if not request.user.mfa:
            return Response({"mfa": "MFA is already disabled"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = DisableMfaSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self._get(request)
