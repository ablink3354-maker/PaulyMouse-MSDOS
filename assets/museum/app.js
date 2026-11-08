/* El Museo de Pauly. Static, offline-first educational adaptation. */
(() => {
  'use strict';
  const D = window.PAULY_DATA;
  const main = document.querySelector('main');
  const modal = document.querySelector('#modal');
  const modalContent = document.querySelector('#modal-content');
  const audio = document.querySelector('#narration');
  const storageKey = 'pauly-museo-v1';
  const defaults = {visited: [], favorites: [], read: [], bestQuiz: 0, settings: {autoplay: false, rate: 1, large: false}};
  let state;
  try { state = JSON.parse(localStorage.getItem(storageKey)) || {}; } catch (_) { state = {}; }
  state = {...defaults, ...state, settings: {...defaults.settings, ...state.settings}};
  for (const key of ['visited', 'favorites', 'read']) if (!Array.isArray(state[key])) state[key] = [];
  let collectionFilter = 'todos', searchText = '', quiz = null, currentTrack = '', toastTimer;
  const animal = id => D.animals.find(a => a.id === id);
  const habitat = id => D.habitats.find(h => h.id === id);
  const escape = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const asset = p => escape(p);
  const norm = s => String(s).normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const countRoom = h => D.animals.filter(a => a.habitat === h && state.visited.includes(a.id)).length;
  function save() { try { localStorage.setItem(storageKey, JSON.stringify(state)); } catch (_) {} }
  function toast(message) { const t = document.querySelector('#toast'); t.textContent = message; t.classList.add('show'); clearTimeout(toastTimer); toastTimer = setTimeout(() => t.classList.remove('show'), 2800); }
  function shuffle(items) { const out = [...items]; for (let i = out.length - 1; i > 0; i--) {const j = Math.floor(Math.random() * (i + 1)); [out[i], out[j]] = [out[j], out[i]];} return out; }
  function listenButton(path, label = 'Escuchar audioguía', extra = '') { return `<button class="btn ${extra}" data-action="listen" data-audio="${asset(path)}" data-label="${escape(label)}"><span aria-hidden="true">▶</span> ${escape(label)}</button>`; }
  function stopAudio() { audio.pause(); currentTrack = ''; updateAudioButtons(); }
  function updateAudioButtons() {
    document.querySelectorAll('[data-audio]').forEach(button => {
      const playing = button.dataset.audio === currentTrack && !audio.paused;
      button.textContent = playing ? 'Ⅱ Pausar narración' : '▶ ' + button.dataset.label;
      button.setAttribute('aria-pressed', String(playing));
    });
  }
  function playTrack(path) {
    if (path === currentTrack && !audio.paused) { audio.pause(); updateAudioButtons(); return; }
    if (path !== currentTrack) { audio.src = path; currentTrack = path; }
    audio.playbackRate = Number(state.settings.rate) || 1;
    audio.play().then(updateAudioButtons).catch(() => { toast('No se pudo reproducir la narración. Inténtalo de nuevo.'); updateAudioButtons(); });
  }
  audio.addEventListener('ended', () => { currentTrack = ''; updateAudioButtons(); });
  audio.addEventListener('pause', updateAudioButtons);
  function roomCard(h, i) {
    return `<a class="room-card" href="#sala/${h.id}"><div class="room-image"><img src="${asset(h.background)}" alt="Ilustración de ${escape(h.name.toLowerCase())}" loading="lazy"><span class="room-number">${String(i+1).padStart(2,'0')}</span></div><div class="room-body"><h3>${escape(h.name)}</h3><p>${escape(h.subtitle)}</p><div class="room-foot"><span>${countRoom(h.id)} / 4 animales descubiertos</span><span aria-hidden="true">Entrar ↗</span></div></div></a>`;
  }
  function animalCard(a) {
    return `<button class="animal-card" data-action="animal" data-id="${a.id}"><img src="${asset(a.photo)}" alt="Fotografía real de ${escape(a.name.toLowerCase())}" loading="lazy">${state.visited.includes(a.id)?'<span class="visited-badge">✓ En tu cuaderno</span>':''}<span class="info"><strong>${escape(a.name)}</strong><small>${escape(habitat(a.habitat).name)} ${state.favorites.includes(a.id)?' · ★':''}</small></span></button>`;
  }
  function home() {
    const visited = state.visited.length, percent = Math.round(visited / D.animals.length * 100);
    main.innerHTML = `<section class="hero"><img class="hero-art" src="assets/backgrounds/bosque.png" alt="Bosque ilustrado con un río, montañas y un árbol hueco"><span class="hero-label">MUSEO INTERACTIVO · EN ESPAÑOL</span><div class="hero-copy"><p class="eyebrow">Para mentes curiosas</p><h1>La naturaleza,<br>de cerca.</h1><p>Acompaña a Pauly por nueve hábitats. Mira animales reales, escucha sus historias y descubre algo nuevo en cada sala.</p><div class="hero-actions"><a class="btn gold" href="#salas">Comenzar la visita ↗</a>${listenButton('assets/audio/bienvenida.mp3','Escuchar a Pauly','outline')}</div></div><img class="mascot" src="assets/pauly.png" alt="Pauly, un ratón explorador con ropa violeta y una brújula"></section>
    <section class="progress-strip" aria-label="Tu visita"><div><strong>Tu cuaderno de visita</strong><small>${visited} de ${D.animals.length} animales descubiertos</small><div class="progress-track" role="progressbar" aria-valuemin="0" aria-valuemax="36" aria-valuenow="${visited}" aria-label="Animales descubiertos"><span style="width:${percent}%"></span></div></div><div><strong>${state.read.length} / 9</strong><small>capítulos guardados</small><a class="quiet" href="#historia">Seguir la historia →</a></div><div><strong>${state.favorites.length} favoritos</strong><small>Los encuentros que quieres recordar</small><a class="quiet" href="#cuaderno">Abrir mi cuaderno →</a></div></section>
    <section class="wrap" id="salas"><div class="section-head"><div><p class="eyebrow">Nueve salas, un solo planeta</p><h2>Elige tu próximo descubrimiento</h2></div><p>No hay un camino obligatorio. Entra a la sala que más curiosidad te dé.</p></div><div class="room-grid">${D.habitats.map(roomCard).join('')}</div><div class="intro-banner"><span class="big-icon" aria-hidden="true">✦</span><div><h3>Una brújula, nueve destinos</h3><p>Escucha la historia de Pauly y reúne los recuerdos de su viaje.</p></div><a class="btn" href="#historia">Conocer la historia →</a></div></section>`;
    if (location.hash === '#salas') requestAnimationFrame(() => document.querySelector('#salas').scrollIntoView());
  }
  function room(id) {
    const h = habitat(id); if (!h) return home();
    main.innerHTML = `<section class="room-stage"><img src="${asset(h.background)}" alt="Escenario ilustrado de ${escape(h.name.toLowerCase())}"><div class="room-title"><p class="eyebrow">Sala ${String(D.habitats.indexOf(h)+1).padStart(2,'0')} · Museo de Pauly</p><h1>${escape(h.name)}</h1><p>${escape(h.subtitle)}. Descubre a cuatro de sus habitantes.</p><div class="room-actions">${listenButton(h.audio,'Escuchar a Pauly','gold')}<a href="#historia/${h.id}" class="btn outline">Historia de esta sala</a></div></div></section><section class="wrap"><p class="breadcrumbs"><a href="#inicio">Museo</a> / ${escape(h.name)}</p><div class="section-head"><div><p class="eyebrow">Fotografías reales · Fichas con voz</p><h2>Conoce a sus habitantes</h2></div><p>Toca una fotografía. Cada animal que conozcas se guardará en tu cuaderno.</p></div><div class="animal-grid">${D.animals.filter(a=>a.habitat===id).map(animalCard).join('')}</div><p class="museum-label">Los fondos son ilustraciones; las fichas muestran fotografías de animales reales. En las regiones polares, cada ficha distingue el Ártico de la Antártida.</p><div class="intro-banner"><span class="big-icon" aria-hidden="true">✧</span><div><h3>¿Qué acabas de descubrir?</h3><p>Prueba un reto de esta sala. Puedes volver a leer las fichas cuando quieras.</p></div><button class="btn" data-action="start-quiz" data-habitat="${id}">Jugar un reto →</button></div></section>`;
  }
  function collection(notebook = false) {
    main.innerHTML = `<section class="wrap"><div class="page-heading"><p class="eyebrow">${notebook?'Tu recorrido, a tu manera':'Una colección para observar y escuchar'}</p><h1>${notebook?'Mi cuaderno de visita':'El mundo animal'}</h1><p>${notebook?'Aquí están los animales que ya conociste y tus favoritos. Tu recorrido se guarda en este dispositivo.':'Treinta y seis animales reales, nueve hábitats y muchas preguntas por descubrir. Busca por nombre o por sala.'}</p></div><input class="search" type="search" id="animal-search" placeholder="Buscar un animal…" aria-label="Buscar un animal" value="${escape(searchText)}"><div class="filters" aria-label="Filtrar colección">${[['todos','Todos'],['vistos','Mi cuaderno'],['favoritos','★ Favoritos'],...D.habitats.map(h=>[h.id,h.name])].map(([id,n])=>`<button class="chip ${collectionFilter===id?'active':''}" aria-pressed="${collectionFilter===id}" data-action="filter" data-filter="${id}">${escape(n)}</button>`).join('')}</div><p class="quiet" id="result-count" aria-live="polite"></p><div class="animal-grid" id="animal-results"></div></section>`;
    renderCollectionGrid();
  }
  function renderCollectionGrid() {
    const results = D.animals.filter(a => {
      const filter = collectionFilter==='todos' || collectionFilter==='vistos'&&state.visited.includes(a.id) || collectionFilter==='favoritos'&&state.favorites.includes(a.id) || collectionFilter===a.habitat;
      return filter && norm(a.name+' '+a.scientific+' '+habitat(a.habitat).name).includes(norm(searchText));
    });
    document.querySelector('#result-count').textContent = `${results.length} animales en esta selección`;
    document.querySelector('#animal-results').innerHTML = results.length ? results.map(animalCard).join('') : '<div class="empty" style="grid-column:1/-1">Aún no hay animales en esta selección. Prueba otro filtro o visita una sala.</div>';
    document.querySelectorAll('[data-filter]').forEach(b => {const active=b.dataset.filter===collectionFilter;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active));});
  }
  function story(id) {
    const h = habitat(id) || D.habitats[0], i = D.habitats.indexOf(h);
    main.innerHTML = `<section class="wrap"><div class="page-heading"><p class="eyebrow">Una historia original para esta adaptación</p><h1>La brújula de los hábitats</h1><p>Pauly descubre que cada lugar guarda una forma distinta de vivir. Lee o escucha el capítulo que quieras.</p></div><div class="story-layout"><nav class="story-list" aria-label="Capítulos">${D.habitats.map((r,j)=>`<a href="#historia/${r.id}" class="story-chapter ${r.id===h.id?'active':''}"><span class="chapter-num">${String(j+1).padStart(2,'0')}</span><span>${escape(r.name)} ${state.read.includes(r.id)?' ✓':''}</span></a>`).join('')}</nav><article class="story-figure"><img src="${asset(h.background)}" alt="Ilustración de ${escape(h.name.toLowerCase())}"><div class="story-text"><p class="eyebrow">Capítulo ${i+1} de 9</p><h2>${escape(h.name)}</h2><p>${escape(h.story)}</p>${listenButton(h.storyAudio,'Escuchar este capítulo')}<div class="story-nav"><button class="btn light" data-action="read-chapter" data-id="${h.id}">${state.read.includes(h.id)?'✓ Capítulo en tu cuaderno':'Guardar capítulo en mi cuaderno'}</button>${i<8?`<a class="btn gold" href="#historia/${D.habitats[i+1].id}">Siguiente capítulo →</a>`:'<a class="btn gold" href="#cuaderno">Ver mi cuaderno →</a>'}</div></div></article></div></section>`;
  }
  function quizView() {
    if (!quiz) {
      main.innerHTML=`<section class="wrap"><div class="page-heading"><p class="eyebrow">Aprende jugando</p><h1>El reto del explorador</h1><p>No hay cronómetro ni vidas que perder. Observa, piensa y vuelve a intentarlo cuando lo necesites.</p></div><div class="quiz-start"><div><h2>¿Listo para sorprenderte?</h2><p>Diez preguntas sobre los animales del museo. Las pistas están en sus fichas.</p><p class="quiet">Tu mejor resultado: ${state.bestQuiz} de 10 respuestas acertadas al primer intento.</p><button class="btn" data-action="start-quiz">Comenzar el recorrido →</button></div><img src="assets/backgrounds/sabana.png" alt="Sabana ilustrada"></div></section>`; return;
    }
    if (quiz.index >= quiz.questions.length) {
      const total=quiz.questions.length;
      if(total===10&&quiz.firstCorrect>state.bestQuiz){state.bestQuiz=quiz.firstCorrect;save();}
      main.innerHTML=`<section class="wrap"><div class="quiz-shell"><div class="quiz-body" style="text-align:center"><p class="eyebrow">Cada pregunta abre una puerta</p><h1>¡Buen recorrido!</h1><p class="summary-score">${quiz.firstCorrect}<span style="font-size:1.5rem"> / ${total}</span></p><p>Respuestas acertadas al primer intento. ¡Ya conoces la respuesta de todas!</p>${listenButton('assets/audio/completo.mp3','Escuchar a Pauly')}<div class="dialog-actions" style="justify-content:center"><button class="btn gold" data-action="restart-quiz">Probar otro reto</button><a class="btn light" href="#coleccion">Volver a la colección</a></div></div></div></section>`;return;
    }
    const a=quiz.questions[quiz.index];
    main.innerHTML=`<section class="wrap"><p class="breadcrumbs"><a href="#inicio">Museo</a> / Reto del explorador</p><div class="quiz-shell"><img class="quiz-image" src="${asset(a.photo)}" alt="Fotografía de ${escape(a.name.toLowerCase())}"><div class="quiz-body"><div class="quiz-top"><span>Pregunta ${quiz.index+1} de ${quiz.questions.length}</span><span>${escape(habitat(a.habitat).name)}</span></div><h2>${escape(a.question)}</h2><p class="quiet">Observa la fotografía y elige una respuesta.</p><div class="answers">${quiz.options.map((answer,i)=>`<button class="answer" data-action="answer" data-index="${i}">${escape(answer)}</button>`).join('')}</div><div id="quiz-feedback" aria-live="polite"></div><div class="dialog-actions"><button class="btn light" data-action="animal" data-id="${a.id}">Leer una pista</button><button class="btn" id="next-question" data-action="next-question" disabled>Siguiente →</button></div></div></div></section>`;
  }
  function startQuiz(h) {
    const pool=h?D.animals.filter(a=>a.habitat===h):D.animals;
    quiz={questions:shuffle(pool).slice(0,10),index:0,firstCorrect:0,attempts:0,solved:false,room:h||null};quiz.options=shuffle(quiz.questions[0].answers);
    if(location.hash==='#retos')quizView();else location.hash='retos';
  }
  function answer(index, button) {
    if(!quiz||quiz.solved)return;
    const a=quiz.questions[quiz.index],correct=quiz.options[index]===a.answers[a.correct];
    quiz.attempts++;
    if(correct){quiz.solved=true;if(quiz.attempts===1)quiz.firstCorrect++;button.classList.add('correct');document.querySelector('#next-question').disabled=false;document.querySelector('#quiz-feedback').innerHTML='<p class="feedback">✓ ¡Muy bien! '+escape(a.fact)+'</p>';if(state.settings.autoplay)playTrack('assets/audio/acierto.mp3');}
    else{button.classList.add('wrong');button.disabled=true;document.querySelector('#quiz-feedback').innerHTML='<p class="feedback">Puedes volver a intentarlo. Pista: '+escape(a.description)+'</p>';}
  }
  function showModal(html) { stopAudio();modalContent.innerHTML='<button class="dialog-close" data-action="close" aria-label="Cerrar">×</button>'+html;modal.setAttribute('aria-labelledby','modal-title');if(!modal.open)modal.showModal(); }
  function detail(id) {
    const a=animal(id);if(!a)return;
    if(!state.visited.includes(id)){state.visited.push(id);save();}
    const c=a.photoCredit||{},favorite=state.favorites.includes(id);
    showModal(`<article class="detail"><img class="detail-photo" src="${asset(a.photo)}" alt="Fotografía real de ${escape(a.name.toLowerCase())}"><div class="detail-copy"><p class="eyebrow">${escape(habitat(a.habitat).name)} · Colección animal</p><h2 id="modal-title">${escape(a.name)}</h2><p class="latin">${escape(a.scientific)}</p><p>${escape(a.description)}</p><div class="fact"><strong>¿Sabías que…?</strong><p style="margin:7px 0 0">${escape(a.fact)}</p></div>${listenButton(a.audio,'Escuchar la ficha')}<div class="dialog-actions"><button class="btn light" data-action="favorite" data-id="${id}" aria-pressed="${favorite}">${favorite?'★ En favoritos':'☆ Guardar favorito'}</button></div><p class="quiet" style="margin-top:18px">✓ Este animal ya está en tu cuaderno.</p><p class="credit-line">Foto: ${escape(c.author||c.attribution||'ver créditos')} · ${escape(c.license||'')} · <a href="${escape(c.source||'#')}" target="_blank" rel="noopener">Fuente y licencia ↗</a></p></div></article>`);
    if(state.settings.autoplay)playTrack(a.audio);
  }
  function settings() {
    showModal(`<div class="modal-simple"><p class="eyebrow">Una visita a tu ritmo</p><h2 id="modal-title">Preferencias</h2><label class="setting"><span>Leer automáticamente las fichas<small class="quiet" style="display:block">Puedes escuchar cada ficha con su botón.</small></span><input id="setting-auto" type="checkbox" ${state.settings.autoplay?'checked':''}></label><label class="setting"><span>Velocidad de narración</span><select id="setting-rate"><option value="0.85" ${state.settings.rate==.85?'selected':''}>Más despacio</option><option value="1" ${state.settings.rate==1?'selected':''}>Normal</option><option value="1.15" ${state.settings.rate==1.15?'selected':''}>Más rápido</option></select></label><label class="setting"><span>Texto más grande</span><input id="setting-large" type="checkbox" ${state.settings.large?'checked':''}></label><p class="quiet" style="margin-top:22px">Tu cuaderno se guarda solamente en este dispositivo. No necesitas una cuenta y no se envían datos de tu visita a un servidor.</p><button class="btn light small" data-action="confirm-reset">Borrar mi cuaderno…</button></div>`);
  }
  function credits() {
    showModal(`<div class="modal-simple"><p class="eyebrow">Sobre esta adaptación</p><h2 id="modal-title">Créditos del museo</h2><p>Adaptación educativa independiente inspirada en <em>Journey Through the Animal Kingdom with Pauly Mouse</em> (1995). El personaje y la obra original pertenecen a sus respectivos titulares. Esta adaptación no reproduce todos los juegos, diálogos ni animaciones de la edición original.</p><p>Las salas, las fichas en español y la historia «La brújula de los hábitats» forman una experiencia educativa nueva. Los fondos y el retrato de Pauly se redibujaron con generación de imágenes por IA a partir de referencias del juego. Las fotografías de la colección son reales.</p><p>Las voces son narraciones sintéticas en español de México: Jorge y Dalia. No imitan las voces originales. Los audios vienen incluidos; no se generan durante la visita.</p><h3>Fotografías y referencias</h3><p class="quiet">Se conserva la licencia de cada fotografía. Al reutilizar los recursos, conserva también estos créditos y cumple sus condiciones.</p>${D.animals.map(a=>{const c=a.photoCredit||{};return `<div class="credit-item"><strong>${escape(a.name)}</strong><br>${escape(c.author||c.attribution||'Autor en la fuente')} · ${escape(c.license||'')}<br><a href="${escape(c.source||'#')}" target="_blank" rel="noopener">Fotografía original ↗</a> ${c.license_url?` · <a href="${escape(c.license_url)}" target="_blank" rel="noopener">Licencia ↗</a>`:''} ${c.reference?` · <a href="${escape(c.reference)}" target="_blank" rel="noopener">Referencia de la especie ↗</a>`:''}</div>`}).join('')}</div>`);
  }
  function render() {
    stopAudio();if(modal.open)modal.close();
    const [route,id]=(location.hash.slice(1)||'inicio').split('/');
    const active=route==='sala'||route==='salas'?'inicio':route==='cuaderno'?'coleccion':route;
    document.querySelectorAll('.desktop-nav a,.bottom-nav a').forEach(a=>{const yes=a.hash==='#'+active;a.classList.toggle('active',yes);if(yes)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});
    document.body.classList.toggle('large-text',!!state.settings.large);
    if(route==='sala')room(id);else if(route==='coleccion'||route==='cuaderno'){if(route==='cuaderno')collectionFilter='vistos';collection(route==='cuaderno');}else if(route==='historia')story(id);else if(route==='retos')quizView();else home();
    if(route!=='salas')window.scrollTo(0,0);updateAudioButtons();
  }
  document.addEventListener('click',event=>{
    const b=event.target.closest('[data-action]');if(!b)return;const action=b.dataset.action;
    if(action==='listen')playTrack(b.dataset.audio);
    else if(action==='animal')detail(b.dataset.id);
    else if(action==='close')modal.close();
    else if(action==='settings')settings();
    else if(action==='credits')credits();
    else if(action==='filter'){collectionFilter=b.dataset.filter;renderCollectionGrid();}
    else if(action==='favorite'){const id=b.dataset.id,i=state.favorites.indexOf(id);if(i<0)state.favorites.push(id);else state.favorites.splice(i,1);save();b.textContent=i<0?'★ En favoritos':'☆ Guardar favorito';b.setAttribute('aria-pressed',String(i<0));}
    else if(action==='read-chapter'){if(!state.read.includes(b.dataset.id)){state.read.push(b.dataset.id);save();toast('Capítulo guardado en tu cuaderno.');}story(b.dataset.id);updateAudioButtons();}
    else if(action==='start-quiz')startQuiz(b.dataset.habitat);
    else if(action==='restart-quiz')startQuiz(quiz?.room);
    else if(action==='answer')answer(Number(b.dataset.index),b);
    else if(action==='next-question'&&quiz?.solved){quiz.index++;quiz.attempts=0;quiz.solved=false;if(quiz.questions[quiz.index])quiz.options=shuffle(quiz.questions[quiz.index].answers);quizView();}
    else if(action==='confirm-reset')showModal('<div class="modal-simple"><h2 id="modal-title">¿Borrar tu cuaderno?</h2><p>Se borrarán los animales descubiertos, favoritos, capítulos y resultados guardados en este dispositivo.</p><div class="dialog-actions"><button class="btn light" data-action="close">Conservar mi cuaderno</button><button class="btn" data-action="reset">Sí, borrar</button></div></div>');
    else if(action==='reset'){state={...defaults,settings:{...state.settings},visited:[],favorites:[],read:[]};save();modal.close();render();toast('Tu cuaderno está listo para una nueva visita.');}
  });
  document.addEventListener('input',event=>{if(event.target.id==='animal-search'){searchText=event.target.value;renderCollectionGrid();}});
  document.addEventListener('change',event=>{const el=event.target;if(el.id==='setting-auto')state.settings.autoplay=el.checked;else if(el.id==='setting-rate')state.settings.rate=Number(el.value);else if(el.id==='setting-large'){state.settings.large=el.checked;document.body.classList.toggle('large-text',el.checked);}else return;save();audio.playbackRate=Number(state.settings.rate)||1;});
  modal.addEventListener('close',()=>{stopAudio();const r=location.hash;if(r.startsWith('#coleccion')||r.startsWith('#cuaderno'))renderCollectionGrid();});
  modal.addEventListener('click',event=>{if(event.target===modal){const r=modal.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)modal.close();}});
  window.addEventListener('hashchange',render);
  document.addEventListener('visibilitychange',()=>{if(document.hidden)audio.pause();});
  render();
  if('serviceWorker' in navigator&&location.protocol.startsWith('http')&&location.hostname!=='pauly.local')navigator.serviceWorker.register('./sw.js').catch(()=>{});
})();
