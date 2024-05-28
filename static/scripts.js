document.addEventListener('DOMContentLoaded', function() {
    let links = document.querySelectorAll('.nav-link');
        for (let i = 0; i < links.length; i++) {
            links[i].addEventListener('click', function() {
                links[i].style.backgroundColor = '#743c74';
            });
        }
  });
