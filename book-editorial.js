(function () {
  const path = window.location.pathname;
  const languagePairs = {
    '/chess-in-the-block.html': [
      { label: 'EN', href: '/chess-in-the-block.html', lang: 'en', active: true },
      { label: 'PT', href: '/xadrez-no-comando.html', lang: 'pt' }
    ],
    '/xadrez-no-comando.html': [
      { label: 'EN', href: '/chess-in-the-block.html', lang: 'en' },
      { label: 'PT', href: '/xadrez-no-comando.html', lang: 'pt', active: true }
    ],
    '/what-still-hurts/': [
      { label: 'EN', href: '/what-still-hurts/', lang: 'en', active: true },
      { label: 'PT', href: '/o-que-ainda-doi.html', lang: 'pt' }
    ],
    '/what-still-hurts/index.html': [
      { label: 'EN', href: '/what-still-hurts/', lang: 'en', active: true },
      { label: 'PT', href: '/o-que-ainda-doi.html', lang: 'pt' }
    ],
    '/o-que-ainda-doi.html': [
      { label: 'EN', href: '/what-still-hurts/', lang: 'en' },
      { label: 'PT', href: '/o-que-ainda-doi.html', lang: 'pt', active: true }
    ]
  };

  function languageMarkup() {
    const choices = languagePairs[path];
    if (!choices) return '';
    return `<span class="book-language-choice" aria-label="Book language">${choices.map(choice =>
      `<a href="${choice.href}" lang="${choice.lang}"${choice.active ? ' aria-current="page"' : ''}>${choice.label}</a>`
    ).join('')}</span>`;
  }

  function installEditorialDesign() {
    document.body.classList.add('book-editorial-page');
    const header = document.createElement('header');
    header.className = 'book-global-header';
    header.innerHTML = `
      <nav class="book-global-nav" aria-label="Main navigation">
        <a class="book-global-brand" href="/">Sabino Pereira<small>Books · Music · Story worlds</small></a>
        <div class="book-global-links">
          <a class="book-home" href="/">Home</a>
          <a href="/books.html" aria-current="page">Books</a>
          <a href="/series.html">Series</a>
          <a href="/music.html">Music</a>
          <a class="book-about" href="/about.html">About</a>
          ${languageMarkup()}
          <a class="book-contact" href="/contact.html">Contact</a>
        </div>
      </nav>`;
    document.body.prepend(header);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', installEditorialDesign);
  } else {
    installEditorialDesign();
  }
})();
