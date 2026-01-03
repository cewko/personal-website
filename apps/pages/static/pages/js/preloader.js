(function() {
  'use strict';

  const initAnimations = () => {
    setTimeout(() => {
      document.body.classList.add('loaded');
    }, 100);
  };

  const initVideo = () => {
    const video = document.getElementById('bg-video');
    if (video) {
      video.play().catch(err => {
        console.log('video autoplay prevented:', err);
      });
    }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      initAnimations();
      initVideo();
    });
  } else {
    initAnimations();
    initVideo();
  }
})();