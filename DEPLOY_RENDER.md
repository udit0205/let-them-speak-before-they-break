# Deploy to a phone-accessible public link

This project is configured for Render Blueprint deployment.

## 1. GitHub
Create a GitHub repository and push the entire `let-them-speak-before-they-break` folder, including `render.yaml`.

## 2. Render
In Render Dashboard choose **New → Blueprint**, select the GitHub repository, then deploy. Render will create the API, frontend, and PostgreSQL resources from `render.yaml`.

## 3. OpenRouter key
When Render prompts for `OPENAI_COMPATIBLE_API_KEY`, paste an OpenRouter API key. The current default model is `openrouter/free`.

## 4. Test
Open the `ltss-api` URL + `/api/health`. It should return JSON with `status: ok`.
Then open the `ltss-web` URL. The site is designed to work in a phone browser.

## 5. Free-tier note
Render currently offers free web services and a free Postgres tier for testing. Free web services can sleep after inactivity, and free Postgres databases expire after 30 days. Use paid resources for a persistent public service.
