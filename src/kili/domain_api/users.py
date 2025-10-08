"""Users domain namespace for the Kili Python SDK."""

import re
from typing import Generator, Iterable, List, Literal, Optional, overload

from typeguard import typechecked

from kili.core.enums import OrganizationRole
from kili.domain.types import ListOrTuple
from kili.domain_api.base import DomainNamespace
from kili.domain_v2.project import IdResponse
from kili.domain_v2.user import UserView, validate_user
from kili.presentation.client.user import UserClientMethods


class UsersNamespace(DomainNamespace):
    """Users domain namespace providing user-related operations.

    This namespace provides access to all user-related functionality
    including querying and managing users and user permissions.

    The namespace provides the following main operations:
    - list(): Query and list users
    - count(): Count users matching filters
    - create(): Create new users
    - update(): Update user properties
    - update_password(): Update user password with enhanced security validation

    Examples:
        >>> kili = Kili()
        >>> # List users in organization
        >>> users = kili.users.list(organization_id="org_id")

        >>> # Count users
        >>> count = kili.users.count(organization_id="org_id")

        >>> # Create a new user
        >>> result = kili.users.create(
        ...     email="newuser@example.com",
        ...     password="securepassword",
        ...     organization_role=OrganizationRole.USER
        ... )

        >>> # Update user properties
        >>> kili.users.update(
        ...     email="user@example.com",
        ...     firstname="John",
        ...     lastname="Doe"
        ... )

        >>> # Update password with security validation
        >>> kili.users.update_password(
        ...     email="user@example.com",
        ...     old_password="oldpass",
        ...     new_password_1="newpass",
        ...     new_password_2="newpass"
        ... )
    """

    def __init__(self, client, gateway):
        """Initialize the users namespace.

        Args:
            client: The Kili client instance
            gateway: The KiliAPIGateway instance for API operations
        """
        super().__init__(client, gateway, "users")

    @overload
    def list(
        self,
        api_key: Optional[str] = None,
        email: Optional[str] = None,
        organization_id: Optional[str] = None,
        fields: ListOrTuple[str] = ("email", "id", "firstname", "lastname"),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: Literal[True],
    ) -> Generator[UserView, None, None]:
        ...

    @overload
    def list(
        self,
        api_key: Optional[str] = None,
        email: Optional[str] = None,
        organization_id: Optional[str] = None,
        fields: ListOrTuple[str] = ("email", "id", "firstname", "lastname"),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: Literal[False] = False,
    ) -> List[UserView]:
        ...

    @typechecked
    def list(
        self,
        api_key: Optional[str] = None,
        email: Optional[str] = None,
        organization_id: Optional[str] = None,
        fields: ListOrTuple[str] = ("email", "id", "firstname", "lastname"),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: bool = False,
    ) -> Iterable[UserView]:
        """Get a generator or a list of users given a set of criteria.

        Args:
            api_key: Query a user by its API Key
            email: Email of the user
            organization_id: Identifier of the user's organization
            fields: All the fields to request among the possible fields for the users.
                See the documentation for all possible fields.
            first: Maximum number of users to return
            skip: Number of skipped users (they are ordered by creation date)
            disable_tqdm: If True, the progress bar will be disabled
            as_generator: If True, a generator on the users is returned.

        Returns:
            An iterable of users.

        Examples:
            >>> # List all users in my organization
            >>> organization = kili.organizations()[0]
            >>> organization_id = organization['id']
            >>> users = kili.users.list(organization_id=organization_id)

            >>> # Get specific user by email
            >>> user = kili.users.list(
            ...     email="user@example.com",
            ...     as_generator=False
            ... )
        """
        # Access the legacy method directly by calling it from the mixin class
        result = UserClientMethods.users(
            self.client,
            api_key=api_key,
            email=email,
            organization_id=organization_id,
            fields=fields,
            first=first,
            skip=skip,
            disable_tqdm=disable_tqdm,
            as_generator=as_generator,  # pyright: ignore[reportGeneralTypeIssues]
        )

        # Wrap results with UserView
        if as_generator:
            # Create intermediate generator - iter() makes result explicitly iterable
            def _wrap_generator() -> Generator[UserView, None, None]:
                result_iter = iter(result)
                for item in result_iter:
                    yield UserView(validate_user(item))

            return _wrap_generator()

        # Convert to list - list() makes result explicitly iterable
        result_list = list(result)
        return [UserView(validate_user(item)) for item in result_list]

    @typechecked
    def count(
        self,
        organization_id: Optional[str] = None,
        api_key: Optional[str] = None,
        email: Optional[str] = None,
    ) -> int:
        """Get user count based on a set of constraints.

        Args:
            organization_id: Identifier of the user's organization.
            api_key: Filter by API Key.
            email: Filter by email.

        Returns:
            The number of users with the parameters provided.

        Examples:
            >>> # Count all users in organization
            >>> count = kili.users.count(organization_id="org_id")

            >>> # Count users by email pattern
            >>> count = kili.users.count(email="user@example.com")
        """
        # Access the legacy method directly by calling it from the mixin class
        return UserClientMethods.count_users(
            self.client,
            organization_id=organization_id,
            api_key=api_key,
            email=email,
        )

    @typechecked
    def create(
        self,
        email: str,
        password: str,
        organization_role: OrganizationRole,
        firstname: Optional[str] = None,
        lastname: Optional[str] = None,
    ) -> IdResponse:
        """Add a user to your organization.

        Args:
            email: Email of the new user, used as user's unique identifier.
            password: On the first sign in, they will use this password and be able to change it.
            organization_role: One of "ADMIN", "USER".
            firstname: First name of the new user.
            lastname: Last name of the new user.

        Returns:
            An IdResponse with the id of the new user.

        Raises:
            ValueError: If email format is invalid or password is weak.

        Examples:
            >>> # Create a new admin user
            >>> result = kili.users.create(
            ...     email="admin@example.com",
            ...     password="securepassword123",
            ...     organization_role=OrganizationRole.ADMIN,
            ...     firstname="John",
            ...     lastname="Doe"
            ... )
            >>> print(result.id)

            >>> # Create a regular user
            >>> result = kili.users.create(
            ...     email="user@example.com",
            ...     password="userpassword123",
            ...     organization_role=OrganizationRole.USER
            ... )
            >>> print(result.id)
        """
        # Validate email format
        if not self._is_valid_email(email):
            raise ValueError(f"Invalid email format: {email}")

        # Validate password strength
        if not self._is_valid_password(password):
            raise ValueError(
                "Password must be at least 8 characters long and contain at least one letter and one number"
            )

        result = UserClientMethods.create_user(
            self.client,
            email=email,
            password=password,
            organization_role=organization_role,
            firstname=firstname,
            lastname=lastname,
        )
        return IdResponse(result)

    @typechecked
    def update(
        self,
        email: str,
        firstname: Optional[str] = None,
        lastname: Optional[str] = None,
        organization_id: Optional[str] = None,
        organization_role: Optional[OrganizationRole] = None,
        activated: Optional[bool] = None,
    ) -> IdResponse:
        """Update the properties of a user.

        Args:
            email: The email is the identifier of the user.
            firstname: Change the first name of the user.
            lastname: Change the last name of the user.
            organization_id: Change the organization the user is related to.
            organization_role: Change the role of the user.
                One of "ADMIN", "TEAM_MANAGER", "REVIEWER", "LABELER".
            activated: In case we want to deactivate a user, but keep it.

        Returns:
            An IdResponse with the user id.

        Raises:
            ValueError: If email format is invalid.

        Examples:
            >>> # Update user's name
            >>> result = kili.users.update(
            ...     email="user@example.com",
            ...     firstname="UpdatedFirstName",
            ...     lastname="UpdatedLastName"
            ... )
            >>> print(result.id)

            >>> # Change user role
            >>> result = kili.users.update(
            ...     email="user@example.com",
            ...     organization_role=OrganizationRole.ADMIN
            ... )
            >>> print(result.id)

            >>> # Deactivate user
            >>> result = kili.users.update(
            ...     email="user@example.com",
            ...     activated=False
            ... )
            >>> print(result.id)
        """
        # Validate email format
        if not self._is_valid_email(email):
            raise ValueError(f"Invalid email format: {email}")

        result = UserClientMethods.update_properties_in_user(
            self.client,
            email=email,
            firstname=firstname,
            lastname=lastname,
            organization_id=organization_id,
            organization_role=organization_role,
            activated=activated,
        )
        return IdResponse(result)

    @typechecked
    def update_password(
        self, email: str, old_password: str, new_password_1: str, new_password_2: str
    ) -> IdResponse:
        """Allow to modify the password that you use to connect to Kili.

        This resolver only works for on-premise installations without Auth0.
        Includes enhanced security validation with additional checks.

        Args:
            email: Email of the person whose password has to be updated.
            old_password: The old password
            new_password_1: The new password
            new_password_2: A confirmation field for the new password

        Returns:
            An IdResponse with the user id.

        Raises:
            ValueError: If validation fails for email, password confirmation,
                       password strength, or security requirements.
            RuntimeError: If authentication fails.
            Exception: If an unexpected error occurs during password update.

        Examples:
            >>> # Update password with security validation
            >>> result = kili.users.update_password(
            ...     email="user@example.com",
            ...     old_password="oldpassword123",
            ...     new_password_1="newpassword456",
            ...     new_password_2="newpassword456"
            ... )
            >>> print(result.id)
        """
        # Enhanced security validation
        self._validate_password_update_request(email, old_password, new_password_1, new_password_2)

        try:
            result = UserClientMethods.update_password(
                self.client,
                email=email,
                old_password=old_password,
                new_password_1=new_password_1,
                new_password_2=new_password_2,
            )
            return IdResponse(result)
        except Exception as e:
            # Enhanced error handling for authentication failures
            if "authentication" in str(e).lower() or "password" in str(e).lower():
                raise RuntimeError(
                    f"Password update failed: Authentication error. "
                    f"Please verify your current password is correct. Details: {e!s}"
                ) from e
            # Re-raise other exceptions as-is
            raise

    def _is_valid_email(self, email: str) -> bool:
        """Validate email format using regex pattern.

        Args:
            email: Email address to validate

        Returns:
            True if email format is valid, False otherwise
        """
        email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        return bool(email_pattern.match(email))

    def _is_valid_password(self, password: str) -> bool:
        """Validate password strength.

        Password must be at least 8 characters long and contain
        at least one letter and one number.

        Args:
            password: Password to validate

        Returns:
            True if password meets requirements, False otherwise
        """
        if len(password) < 8:
            return False

        has_letter = any(c.isalpha() for c in password)
        has_number = any(c.isdigit() for c in password)

        return has_letter and has_number

    def _validate_password_update_request(
        self, email: str, old_password: str, new_password_1: str, new_password_2: str
    ) -> None:
        """Validate password update request with enhanced security checks.

        Args:
            email: Email of the user
            old_password: Current password
            new_password_1: New password
            new_password_2: New password confirmation

        Raises:
            ValueError: If any validation check fails
        """
        # Validate email format
        if not self._is_valid_email(email):
            raise ValueError(f"Invalid email format: {email}")

        # Check that passwords are not empty
        if not old_password:
            raise ValueError("Current password cannot be empty")

        if not new_password_1:
            raise ValueError("New password cannot be empty")

        if not new_password_2:
            raise ValueError("Password confirmation cannot be empty")

        # Check password confirmation matches
        if new_password_1 != new_password_2:
            raise ValueError("New password confirmation does not match")

        # Validate new password strength
        if not self._is_valid_password(new_password_1):
            raise ValueError(
                "New password must be at least 8 characters long and contain at least one letter and one number"
            )

        # Security check: new password should be different from old password
        if old_password == new_password_1:
            raise ValueError("New password must be different from the current password")

        # Additional security checks
        if len(new_password_1) > 128:
            raise ValueError("Password cannot be longer than 128 characters")

        # Check for common weak patterns
        if self._is_weak_password(new_password_1):
            raise ValueError(
                "Password is too weak. Avoid common patterns like '123456', 'password', or repeated characters"
            )

    def _is_weak_password(self, password: str) -> bool:
        """Check for common weak password patterns.

        Args:
            password: Password to check

        Returns:
            True if password is considered weak, False otherwise
        """
        # Convert to lowercase for case-insensitive checks
        lower_password = password.lower()

        # Common weak passwords
        weak_passwords = [
            "password",
            "12345678",
            "qwerty",
            "abc123",
            "letmein",
            "welcome",
            "monkey",
            "dragon",
            "master",
            "admin",
        ]

        if lower_password in weak_passwords:
            return True

        # Check for repeated characters (e.g., "aaaaaaaa")
        if len(set(password)) < 3:
            return True

        # Check for simple sequences (e.g., "abcdefgh", "12345678")
        if self._has_simple_sequence(password):
            return True

        return False

    def _has_simple_sequence(self, password: str) -> bool:
        """Check if password contains simple character sequences.

        Args:
            password: Password to check

        Returns:
            True if password contains simple sequences, False otherwise
        """
        # Check for ascending sequences
        for i in range(len(password) - 3):
            sequence = password[i : i + 4]
            if len(sequence) == 4:
                # Check if it's an ascending numeric sequence
                if sequence.isdigit():
                    if all(int(sequence[j]) == int(sequence[j - 1]) + 1 for j in range(1, 4)):
                        return True
                # Check if it's an ascending alphabetic sequence
                elif sequence.isalpha():
                    if all(ord(sequence[j]) == ord(sequence[j - 1]) + 1 for j in range(1, 4)):
                        return True

        return False
