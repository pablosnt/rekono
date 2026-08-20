# Security Policy

Rekono is a distributed application that performs dangerous operations like executing tools dynamically and handles very sensitive data, such as:

- User information
- Target scope
- Assets and security vulnerabilities detected on the targets
- Authentication credentials on the targets and integrations

Considering these facts and that Rekono is a cybersecurity project, we are very concerned about keeping the platform safe, so security is our number one priority. We encourage everyone to find and responsibly report security issues in this project.

## Reporting

**Never report a security vulnerability through a public channel**, like a GitHub issue, a Pull Request or the Discord server. Their content is public, and it can be used by attackers to exploit the vulnerability before a fix is available.

Use one of these private channels instead:

| Channel | How | When to use it |
| --- | --- | --- |
| GitHub Security Advisories | [Report a vulnerability](https://github.com/pablosnt/rekono/security/advisories/new) | Preferred. Only you and the maintainers can see it, and the whole process is managed there |
| Email | [rekono.project@gmail.com](mailto:rekono.project@gmail.com) | If you don't have a GitHub account or you prefer email |

Note that security fixes are only released for the latest version of Rekono. Before reporting an issue, please check that it still affects the [latest release](https://github.com/pablosnt/rekono/releases/latest) or the `develop` branch.

## Rules

- Test only against Rekono installations where you are authorized to perform security tests
- If you access data that is not yours during your research, stop there, don't store it and tell us about it in the report
- Give us a reasonable time to release a fix before publishing any detail about the vulnerability

We won't take any legal action against researchers that follow this policy, and we will do our best to work with you.

## Process

This is how we will manage your reports:

1. Acknowledgement: we confirm that we received your report, sooner rather than later
2. Triage: we try to reproduce the issue and confirm that it's accepted. If we need more information or if it's rejected, we let you know
3. Advisory: if you did not report it via an advisory, we will create a [security advisory](https://github.com/pablosnt/rekono/security/advisories) and invite you to it, so you can follow the progress and review the fix
4. Fix: we develop and release the fix as soon as we can
5. Disclosure: we publish the advisory after releasing the fix, and add it to the [CHANGELOG](CHANGELOG.md)
6. Credits: you are credited as the reporter in the advisory and in the release notes, unless you prefer to stay anonymous

Unfortunately, Rekono is maintained by a very small team in their free time with no external funds, so we can't offer any economic reward for the reports.


Thank you for helping us to keep Rekono safe! :heart: