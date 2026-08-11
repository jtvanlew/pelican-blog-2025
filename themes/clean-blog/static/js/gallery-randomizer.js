// gallery-randomizer.js
// Randomize row groupings for .pswp-gallery elements when they contain 5+ items.
// Algorithm: generate a sequence of group sizes (1..4) that sum to N, preferring 2/3,
// then assign bootstrap column classes accordingly (col-xs-12/6/4/3).

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

  function applyPatternToGallery(gallery, pattern) {
    // items are the direct child divs (each item wrapper)
    var items = Array.prototype.slice.call(gallery.querySelectorAll(':scope > div'));
    // remove existing col-* classes and apply new ones row by row
    var idx = 0;
    for (var r = 0; r < pattern.length; r++) {
      var group = pattern[r];
      var col = 12 / group; // integer for group in 1,2,3,4
      for (var j = 0; j < group; j++) {
        var el = items[idx];
        if (!el) break;
        // remove any col-xxx- classes (simple regex)
        el.className = el.className.replace(/col-(xs|sm|md|lg)-\d+\b/g, '').trim();
        // add new responsive classes
        el.classList.add('col-xs-' + col);
        el.classList.add('col-sm-' + col);
        el.classList.add('col-md-' + col);
        idx++;
      }
    }
  }

  function processGalleries() {
    var galleries = document.querySelectorAll('.pswp-gallery');
    galleries.forEach(function (g) {
      try {
  var items = g.querySelectorAll(':scope > div');
  // activate for galleries with 5 or more images
  if (!items || items.length < 5) return;
        var n = items.length;
        var pattern = generatePattern(n);
        applyPatternToGallery(g, pattern);
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
