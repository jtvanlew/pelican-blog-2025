// gallery-randomizer.js
// Randomize row groupings for .pswp-gallery elements (5+ items, or any with a
// featured photo). Featured photos (.gallery-featured, from digiKam ratings) keep a
// full-width row; the runs of other photos between them get a random sequence of
// group sizes (1..4, preferring 2/3) as bootstrap column classes (col-xs-12/6/4/3).

(function () {
  'use strict';

  function weightedRandomChoice(choices) {
    // choices: array of [value, weight]
    var total = choices.reduce(function (s, c) { return s + c[1]; }, 0);
    var r = Math.random() * total;
    for (var i = 0; i < choices.length; i++) {
      r -= choices[i][1];
      if (r <= 0) return choices[i][0];
    }
    return choices[choices.length - 1][0];
  }

  function generatePattern(n) {
    var result = [];
    var remaining = n;
    var attempts = 0;
    // Special-case n == 5: prefer a balanced 2+3 or 3+2 grouping to avoid a lone singleton
    if (n === 5) {
      return (Math.random() < 0.5) ? [2, 3] : [3, 2];
    }
    while (remaining > 0 && attempts < 1000) {
      attempts++;
      if (remaining <= 3) {
        // finish with the remainder to avoid tiny leftovers
        result.push(remaining);
        break;
      }
      // prefer 2 and 3, rarely 1
      var s = weightedRandomChoice([[2, 0.5], [3, 0.4], [1, 0.1]]);
      // if s is too large, fallback
      if (s > remaining) s = remaining;
      // avoid leaving a remainder of 1 too often: if choosing s leads to remaining-s == 1,
      // prefer choosing a different s (unless remaining is small)
      if (remaining - s === 1 && remaining > 4) {
        // try a different s
        s = (s === 2) ? 3 : 2;
        if (s > remaining) s = 1;
      }
      result.push(s);
      remaining -= s;
    }
    return result;
  }

  function setCols(el, col) {
    // remove any col-xxx- classes, then add responsive ones
    el.className = el.className.replace(/col-(xs|sm|md|lg)-\d+\b/g, '').trim();
    el.classList.add('col-xs-' + col);
    el.classList.add('col-sm-' + col);
    el.classList.add('col-md-' + col);
  }

  function applyPattern(items, pattern) {
    var idx = 0;
    for (var r = 0; r < pattern.length; r++) {
      var group = pattern[r];
      var col = 12 / group; // integer for group in 1,2,3,4
      for (var j = 0; j < group && idx < items.length; j++) {
        setCols(items[idx], col);
        idx++;
      }
    }
  }

  function patternFor(n) {
    if (n === 4) return [2, 2];
    return generatePattern(n);
  }

  function processGalleries() {
    var galleries = document.querySelectorAll('.pswp-gallery');
    galleries.forEach(function (g) {
      try {
        var items = Array.prototype.slice.call(g.querySelectorAll(':scope > div'));
        var hasFeatured = items.some(function (el) { return el.classList.contains('gallery-featured'); });
        // small galleries keep their server-side layout unless a photo is featured
        if (items.length < 5 && !hasFeatured) return;
        // Featured photos (digiKam rating) always get a full-width row of their own;
        // shuffle the runs of ordinary photos between them.
        var run = [];
        var flush = function () {
          if (run.length) applyPattern(run, patternFor(run.length));
          run = [];
        };
        items.forEach(function (el) {
          if (el.classList.contains('gallery-featured')) {
            flush();
            setCols(el, 12);
          } else {
            run.push(el);
          }
        });
        flush();
      } catch (e) {
        // fail silently
        console && console.error && console.error('gallery-randomizer error', e);
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', processGalleries);
  } else {
    processGalleries();
  }
})();
