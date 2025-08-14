export function ready(callback) {
  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    callback();
    return;
  }
  document.addEventListener('DOMContentLoaded', callback, { once: true });
}


