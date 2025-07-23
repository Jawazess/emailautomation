# Email Automation

This repository provides a basic example of automating email workflows using Python and a minimal front-end interface. Originally it only created Gmail drafts from a CSV file, but it has been extended to optionally send the emails directly via SMTP. A simple React based page allows importing the CSV file, uploading it to the backend and either creating drafts or sending the emails in order. A Google sign‑in button can be used to authorize the application for creating and sending messages through the Gmail API.

To enable Google authentication, define a `GOOGLE_CLIENT_ID` global variable in `public/index.html` with your OAuth client ID. The sign-in button will request access to send email on behalf of the signed in user and the resulting token is passed to the backend API.

## Deploying to Vercel

The repository is configured for [Vercel](https://vercel.com) so it can be hosted online. The Python API lives in the `api/` directory and the static front‑end resides in `public/`.

1. Install the Vercel CLI with `npm i -g vercel`.
2. Run `vercel` in the project root and follow the prompts.
3. The application will be available at your Vercel URL with API endpoints under `/api`.
