# Quiet Thought Workflow

Use this checklist whenever you publish a new Quiet Thought.

## 1. Create the article page

Duplicate `quiet-thought-template.html` and rename it with a clear slug:

- `quiet-thought-why-clarity-compounds.html`
- `quiet-thought-discipline-without-drama.html`

Then replace every `{{PLACEHOLDER}}` in the template.

## 2. Keep the SEO fields tight

- `{{THOUGHT_TITLE}}`: exact article title.
- `{{META_DESCRIPTION}}`: around 140 to 160 characters.
- `{{OG_DESCRIPTION}}`: one clean sentence for sharing previews.
- `{{PAGE_SLUG}}`: filename without `.html`.
- `{{OG_IMAGE_FILE}}`: social image filename inside `/images/`.
- `{{THOUGHT_HOOK}}`: short line under the title.
- `{{THOUGHT_SUBTITLE}}`: one sentence expanding the angle of the piece.

## 3. Add the article to the index page

In `ideas.html`:

- Add a new `.idea-card`
- Set `data-page-url` to the new article URL
- Add a `Read article` link inside `.idea-card-actions`
- Keep the short preview on the card

## 4. Create the social image

Create a matching OG image in `/images/`, ideally reusing the same editorial system:

- `og-quiet-thought-what-is-clarity.svg`
- `og-quiet-thought-discipline-without-drama.svg`

Use the image filename in `{{OG_IMAGE_FILE}}`.

## 5. Add the article to the sitemap

In `sitemap.xml`, add:

```xml
<url>
  <loc>https://sabinopereira.com/{{PAGE_SLUG}}.html</loc>
</url>
```

## 6. Add at least one internal link

Link to the new thought from at least one existing page, ideally:

- `index.html`
- `ideas.html`
- another `quiet-thought-*.html` page

## 7. Share setup

The template already includes:

- canonical URL
- Open Graph tags
- Twitter tags
- `Article` structured data
- share buttons wired to the final article URL

## 8. Final pre-publish check

- Title matches the article and slug
- Description is unique
- OG image is unique and referenced in the page
- The article is linked from `ideas.html`
- The article is in `sitemap.xml`
- At least one other page links to it
- Share preview points to the article URL, not `ideas.html`
