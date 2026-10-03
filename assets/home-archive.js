/* word&music — Random selection of 3 past concerts on home scene */
(function () {
  var container = document.querySelector('#past-concerts .cards3');
  if (!container) return;

  var isEn = document.documentElement.lang === 'en';
  var prefix = isEn ? '/en' : '';

  var concerts = [
    {
      slug: 'vivre-aimer-rever',
      title: 'Vivre, Aimer, Rêver…',
      meta: '03.10.2026 · 16:00–17:00',
      aria: isEn ? 'Open concert Vivre, Aimer, Rêver…' : 'Відкрити концерт Vivre, Aimer, Rêver…',
      picture: {
        light: '/assets/img/vivre-banner-20261003-current-light-320.webp 320w, /assets/img/vivre-banner-20261003-current-light-480.webp 480w, /assets/img/vivre-banner-20261003-current-light-720.webp 720w, /assets/img/vivre-banner-20261003-current-light-960.webp 960w, /assets/img/vivre-banner-20261003-current-light-1440.webp 1440w, /assets/img/vivre-banner-20261003-current-light.jpg 1920w',
        dark: '/assets/img/vivre-banner-20261003-current-night-320.webp 320w, /assets/img/vivre-banner-20261003-current-night-480.webp 480w, /assets/img/vivre-banner-20261003-current-night-720.webp 720w, /assets/img/vivre-banner-20261003-current-night-960.webp 960w, /assets/img/vivre-banner-20261003-current-night-1440.webp 1440w, /assets/img/vivre-banner-20261003-current-night.jpg 1920w',
        src: '/assets/img/vivre-banner-20261003-current-night.jpg'
      }
    },
    {
      slug: 'winter-extravaganza',
      title: isEn ? 'Winter Extravaganza' : 'Зимова феєрія',
      meta: '25.12.2023',
      aria: isEn ? 'Open concert “Winter Extravaganza”' : 'Відкрити концерт «Зимова феєрія»',
      src: '/assets/img/yt-bpz1jSrtFMA.jpg',
      srcset: '/assets/img/yt-bpz1jSrtFMA-320.webp 320w, /assets/img/yt-bpz1jSrtFMA-480.webp 480w, /assets/img/yt-bpz1jSrtFMA-720.webp 720w, /assets/img/yt-bpz1jSrtFMA-960.webp 960w, /assets/img/yt-bpz1jSrtFMA.jpg 1280w'
    },
    {
      slug: 'christmas-kaleidoscope',
      title: isEn ? 'Christmas Kaleidoscope' : 'Різдвяний Калейдоскоп',
      meta: '21.12.2024',
      aria: isEn ? 'Open concert “Christmas Kaleidoscope”' : 'Відкрити концерт «Різдвяний Калейдоскоп»',
      src: '/assets/img/yt-JAMDscAMvQA.jpg',
      srcset: '/assets/img/yt-JAMDscAMvQA-320.webp 320w, /assets/img/yt-JAMDscAMvQA-480.webp 480w, /assets/img/yt-JAMDscAMvQA-720.webp 720w, /assets/img/yt-JAMDscAMvQA-960.webp 960w, /assets/img/yt-JAMDscAMvQA.jpg 1280w'
    },
    {
      slug: 'music-of-soul-and-heart',
      title: isEn ? 'Music of Soul and Heart' : 'Музика душі і серця',
      meta: '26.08.2023',
      aria: isEn ? 'Open concert “Music of Soul and Heart”' : 'Відкрити концерт «Музика душі і серця»',
      src: '/assets/img/yt-474f5Yrp5-o.jpg',
      srcset: '/assets/img/yt-474f5Yrp5-o-320.webp 320w, /assets/img/yt-474f5Yrp5-o-480.webp 480w, /assets/img/yt-474f5Yrp5-o-720.webp 720w, /assets/img/yt-474f5Yrp5-o-960.webp 960w, /assets/img/yt-474f5Yrp5-o.jpg 1280w'
    },
    {
      slug: 'autumn-rendezvous',
      title: isEn ? 'Autumn Rendezvous' : 'Осіннє побачення',
      meta: '15.11.2025',
      aria: isEn ? 'Open concert “Autumn Rendezvous”' : 'Відкрити концерт «Осіннє побачення»',
      src: '/assets/img/autumn-rendezvous-16x9.jpg',
      srcset: '/assets/img/autumn-rendezvous-16x9-320.webp 320w, /assets/img/autumn-rendezvous-16x9-480.webp 480w, /assets/img/autumn-rendezvous-16x9-720.webp 720w, /assets/img/autumn-rendezvous-16x9-960.webp 960w, /assets/img/autumn-rendezvous-16x9.jpg 1280w'
    },
    {
      slug: 'roads-of-love',
      title: isEn ? 'Roads of Love' : 'Дороги кохання',
      meta: '08.06.2024',
      aria: isEn ? 'Open concert “Roads of Love”' : 'Відкрити концерт «Дороги кохання»',
      src: '/assets/img/roads-of-love-16x9.jpg',
      srcset: '/assets/img/roads-of-love-16x9-320.webp 320w, /assets/img/roads-of-love-16x9-480.webp 480w, /assets/img/roads-of-love-16x9-720.webp 720w, /assets/img/roads-of-love-16x9-960.webp 960w, /assets/img/roads-of-love-16x9.jpg 1280w'
    },
    {
      slug: 'melodies-of-enchanting-june',
      title: isEn ? 'Melodies of Enchanting June' : 'Мелодії чарівного червня',
      meta: '02.06.2025',
      aria: isEn ? 'Open concert “Melodies of Enchanting June”' : 'Відкрити концерт «Мелодії чарівного червня»',
      src: '/assets/img/melodies-of-enchanting-june-16x9.jpg',
      srcset: '/assets/img/melodies-of-enchanting-june-16x9-320.webp 320w, /assets/img/melodies-of-enchanting-june-16x9-480.webp 480w, /assets/img/melodies-of-enchanting-june-16x9-720.webp 720w, /assets/img/melodies-of-enchanting-june-16x9-960.webp 960w, /assets/img/melodies-of-enchanting-june-16x9.jpg 1280w'
    },
    {
      slug: 'amore-eterno',
      title: 'Amore Eterno',
      meta: '29.07.2023',
      aria: isEn ? 'Open concert “Amore Eterno”' : 'Відкрити концерт «Amore Eterno»',
      src: '/assets/img/yt-qU1Jl_9ZuGQ.jpg',
      srcset: '/assets/img/yt-qU1Jl_9ZuGQ-320.webp 320w, /assets/img/yt-qU1Jl_9ZuGQ-480.webp 480w, /assets/img/yt-qU1Jl_9ZuGQ-720.webp 720w, /assets/img/yt-qU1Jl_9ZuGQ-960.webp 960w, /assets/img/yt-qU1Jl_9ZuGQ.jpg 1280w'
    },
    {
      slug: 'heartstrings',
      title: isEn ? 'Heartstrings' : 'Струни серця',
      meta: '10.06.2023',
      aria: isEn ? 'Open concert “Heartstrings”' : 'Відкрити концерт «Струни серця»',
      src: '/assets/img/yt-UaWqVU8fUw4.jpg',
      srcset: '/assets/img/yt-UaWqVU8fUw4-320.webp 320w, /assets/img/yt-UaWqVU8fUw4-480.webp 480w, /assets/img/yt-UaWqVU8fUw4-720.webp 720w, /assets/img/yt-UaWqVU8fUw4-960.webp 960w, /assets/img/yt-UaWqVU8fUw4.jpg 1280w'
    },
    {
      slug: 'soul-wanderings',
      title: isEn ? 'Where the Soul Wanders' : 'Де блукає душа',
      meta: '14.02.2026',
      aria: isEn ? 'Open concert “Where the Soul Wanders”' : 'Відкрити концерт «Де блукає душа»',
      src: '/assets/img/soul-wanderings-poster.jpg',
      srcset: '/assets/img/soul-wanderings-poster-320.webp 320w, /assets/img/soul-wanderings-poster-480.webp 480w, /assets/img/soul-wanderings-poster-720.webp 720w, /assets/img/soul-wanderings-poster-960.webp 960w, /assets/img/soul-wanderings-poster-1440.webp 1440w, /assets/img/soul-wanderings-poster.jpg 1448w',
      style: 'object-position:50% 58%'
    },
    {
      slug: 'stabat-mater',
      title: 'Stabat Mater',
      meta: '16.04.2025',
      aria: isEn ? 'Open concert “Stabat Mater”' : 'Відкрити концерт «Stabat Mater»',
      src: '/assets/img/stabat-mater-poster.jpg',
      srcset: '/assets/img/stabat-mater-poster-320.webp 320w, /assets/img/stabat-mater-poster-480.webp 480w, /assets/img/stabat-mater-poster-720.webp 720w, /assets/img/stabat-mater-poster-960.webp 960w, /assets/img/stabat-mater-poster-1440.webp 1440w, /assets/img/stabat-mater-poster.jpg 1448w',
      style: 'object-position:50% 44%'
    },
    {
      slug: 'melodies-eternelles',
      title: 'Mélodies éternelles',
      meta: '03.08.2025',
      aria: isEn ? 'Open concert “Mélodies éternelles”' : 'Відкрити концерт «Mélodies éternelles»',
      src: '/assets/img/melodies-eternelles-poster.jpg',
      srcset: '/assets/img/melodies-eternelles-poster-320.webp 320w, /assets/img/melodies-eternelles-poster-480.webp 480w, /assets/img/melodies-eternelles-poster-720.webp 720w, /assets/img/melodies-eternelles-poster-960.webp 960w, /assets/img/melodies-eternelles-poster.jpg 1440w',
      style: 'object-position:50% 24%'
    }
  ];

  // Fisher-Yates shuffle
  var pool = concerts.slice();
  for (var i = pool.length - 1; i > 0; i--) {
    var j = Math.floor(Math.random() * (i + 1));
    var temp = pool[i];
    pool[i] = pool[j];
    pool[j] = temp;
  }
  var selected = pool.slice(0, 3);

  function renderCard(c) {
    var href = prefix + '/concerts/' + c.slug + '.html';
    var picHtml = '';
    if (c.picture) {
      picHtml = '<picture>' +
        '<source media="(prefers-color-scheme: dark)" srcset="' + c.picture.light + '" sizes="(max-width:900px) 76vw, 31vw">' +
        '<img src="' + c.picture.src + '" srcset="' + c.picture.dark + '" alt="" loading="lazy" sizes="(max-width:900px) 76vw, 31vw" data-motion-ready="">' +
        '</picture>';
    } else {
      var styleAttr = c.style ? ' style="' + c.style + '"' : '';
      picHtml = '<img src="' + c.src + '" srcset="' + c.srcset + '" alt="" loading="lazy" sizes="(max-width:900px) 76vw, 31vw"' + styleAttr + ' data-motion-ready="">';
    }

    return '<article class="card">' +
      '<a class="pic" href="' + href + '" aria-label="' + c.aria + '">' + picHtml + '</a>' +
      '<div class="meta muted" style="margin-top:16px">' + c.meta + '</div>' +
      '<a class="t tem" href="' + href + '">' + c.title + '</a>' +
      '</article>';
  }

  container.innerHTML = selected.map(renderCard).join('\n');
})();
