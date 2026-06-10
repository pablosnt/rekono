# Email Templates

Email templates using [react-email](https://react.email/) with Tailwind CSS. Django renders them server-side, so Django template syntax (`{{ variable }}`, `{% tag %}`) is embedded as literal strings inside the React components and survives the build step untouched.

## Install dependencies

```bash
pnpm install
```

## Development

```bash
pnpm dev
```

This deploys a development server in https://localhost:3000 where we can explore the templates preview.

## Generating templates

```bash
pnpm build
```

This exports each component to a Django-compatible `.html` file in this directory.

The build runs automatically as part of the Docker image (`build-email-templates` stage) and on CI for any pull request that touches `email-templates/**`.

## Templates

| File                                     | Purpose                                                 |
| ---------------------------------------- | ------------------------------------------------------- |
| `alert_notification.html`                | Alert triggered by a matching security finding          |
| `execution_notification.html`            | Security tool execution completed with findings summary |
| `report_created.html`                    | Security report generated and ready to download         |
| `user_enable_account.html`               | User account has been enabled                           |
| `user_invitation.html`                   | New user invitation with account setup link             |
| `user_login_notification.html`           | New login detected on user account                      |
| `user_mfa.html`                          | Multi-factor authentication one-time password           |
| `user_password_reset.html`               | Password reset request with secure link                 |
| `user_telegram_linked_notification.html` | Telegram bot successfully linked to account             |
