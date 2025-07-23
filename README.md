# Email Automation

This repository provides a basic example of automating email workflows using Python and a minimal front-end interface. Originally it only created Gmail drafts from a CSV file, but it has been extended to optionally send the emails directly via SMTP. A simple React based page allows importing the CSV file, uploading it to the backend and either creating drafts or sending the emails in order.

## Deploying to Vercel

The repository is configured for [Vercel](https://vercel.com) so it can be hosted online. The Python API lives in the `api/` directory and the static front‑end resides in `public/`.

1. Install the Vercel CLI with `npm i -g vercel`.
2. Run `vercel` in the project root and follow the prompts.
3. The application will be available at your Vercel URL with API endpoints under `/api`.
