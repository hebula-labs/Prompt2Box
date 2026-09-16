# Security Policy

## Supported versions

Prompt2Box is pre-1.0. Security fixes land on `main` and ship in the next
release; older releases are not patched.

| Version        | Supported |
| -------------- | --------- |
| Latest release | Yes       |
| Older releases | No        |

## Reporting a vulnerability

**Please do not report security problems through public issues, discussions,
or pull requests.**

Report them privately through GitHub's vulnerability reporting for this
repository:

https://github.com/hebula-labs/Prompt2Box/security/advisories/new

Include the Prompt2Box version, a description of the issue, steps or a proof of
concept to reproduce it, and the impact you believe it has. Never include a real
API key in a report.

What you can expect from us:

- Acknowledgement within 3 business days.
- An assessment, and a fix timeline if the report is confirmed, within 10
  business days.
- Credit in the advisory and release notes, unless you prefer to stay anonymous.

We ask that you give us reasonable time to ship a fix before disclosing the
issue publicly.

## Scope

In scope: the `prompt2box` package and CLI, including how it handles API keys,
`.env` files, local image files, and the files it writes.

Out of scope:

- The Gemini API and Vertex AI themselves. Report those to Google at
  https://bughunters.google.com.
- The accuracy or content of model output.
- Vulnerabilities in third-party dependencies. Report those upstream; Dependabot
  tracks them for this repository.

## Handling credentials safely

- Prompt2Box reads `GEMINI_API_KEY` / `GOOGLE_API_KEY` from the environment, or
  from a `.env` file in the working directory. It never writes keys to disk and
  does not log them.
- A key passed on the command line with `--api-key` can be visible in shell
  history and process listings. Prefer the environment variable or a `.env`
  file, and keep `.env` out of version control (it is in `.gitignore`).
- Images are uploaded to Google's API for detection. Do not send images you are
  not permitted to share with that service.
