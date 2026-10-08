/* N-STUDIO · demos médicas: menú, formulario de orientación → WhatsApp, mapa bajo demanda */
(function () {
  'use strict';

  var body = document.body;
  var WA = body.getAttribute('data-wa');
  var DOCTOR = body.getAttribute('data-doctor') || 'Doctor';

  /* Menú móvil */
  var btn = document.querySelector('.menu-btn');
  var links = document.getElementById('menu');
  if (btn && links) {
    var close = function () {
      links.classList.remove('is-open');
      btn.setAttribute('aria-expanded', 'false');
    };
    btn.addEventListener('click', function () {
      var open = links.classList.toggle('is-open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    links.addEventListener('click', function (e) {
      if (e.target.closest('a')) close();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') close();
    });
  }

  /* Formulario de orientación: arma el mensaje y abre WhatsApp (no envía datos a ningún servidor) */
  var form = document.getElementById('orientacion');
  if (form && WA) {
    var zona = form.querySelector('#zona');
    var zonaErr = form.querySelector('#zona-error');
    var detalle = form.querySelector('#detalle');

    var setError = function (msg) {
      zonaErr.textContent = msg;
      if (msg) {
        zona.setAttribute('aria-invalid', 'true');
      } else {
        zona.removeAttribute('aria-invalid');
      }
    };
    zona.addEventListener('change', function () {
      if (zona.value) setError('');
    });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!zona.value) {
        setError('Elija qué le gustaría consultar para poder orientarle.');
        zona.focus();
        return;
      }
      setError('');
      var tiempo = form.querySelector('input[name="tiempo"]:checked');
      var estudios = form.querySelector('input[name="estudios"]:checked');
      var lineas = [
        'Hola ' + DOCTOR + ', quisiera agendar una consulta.',
        '- Motivo: ' + zona.value
      ];
      if (tiempo) lineas.push('- Desde hace: ' + tiempo.value);
      if (estudios) lineas.push('- Estudios previos: ' + estudios.value);
      var extra = detalle && detalle.value.trim();
      if (extra) lineas.push('- Detalle: ' + extra.slice(0, 400));
      lineas.push('¿Qué días tiene disponibles?');
      var url = 'https://wa.me/' + WA + '?text=' + encodeURIComponent(lineas.join('\n'));
      window.open(url, '_blank', 'noopener');
    });
  }

  /* Mapa: se carga solo al pulsar (sin cookies de Google hasta entonces) */
  var mapBtn = document.querySelector('[data-load-map]');
  if (mapBtn) {
    mapBtn.addEventListener('click', function () {
      var box = mapBtn.closest('.map');
      var q = encodeURIComponent(mapBtn.getAttribute('data-load-map'));
      var iframe = document.createElement('iframe');
      iframe.src = 'https://www.google.com/maps?q=' + q + '&output=embed';
      iframe.title = 'Mapa de ubicación del consultorio';
      iframe.loading = 'lazy';
      iframe.referrerPolicy = 'no-referrer-when-downgrade';
      box.textContent = '';
      box.appendChild(iframe);
    });
  }

  /* Año del pie */
  var y = document.getElementById('year');
  if (y) y.textContent = String(new Date().getFullYear());
})();
