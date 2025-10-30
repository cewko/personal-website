(function() {
  'use strict';

  const initAnimations = () => {
    setTimeout(() => {
      document.body.classList.add('loaded');
    }, 100);
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAnimations);
  } else {
    initAnimations();
  }
})();