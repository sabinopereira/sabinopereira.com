# sabinopereira.com

## Quiet Signal Deploy

`Quiet Signal` now expects a private endpoint at `/api/quiet-news`.

If you deploy on Vercel:

1. Import this project into Vercel.
2. Add one environment variable:
   `GNEWS_API_KEY`
3. Redeploy.

After that, the app can call the private endpoint and the API key stays on the server side instead of the browser.

If `GNEWS_API_KEY` is missing, the app can still run in local test mode by saving a key in the browser on the setup card.

## Quiet Thoughts

For new SEO-ready Quiet Thoughts, use:

- `quiet-thought-template.html`
- `quiet-thought-workflow.md`
