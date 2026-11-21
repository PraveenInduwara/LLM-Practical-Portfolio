(() => {
  'use strict';

  const STORAGE_KEY = 'shareshelf-v1';
  const DAY_MS = 24 * 60 * 60 * 1000;
  const foodEmojis = {
    avocado: '🥑', apple: '🍎', apples: '🍎', banana: '🍌', bananas: '🍌', bread: '🍞', carrot: '🥕', carrots: '🥕', cheese: '🧀', egg: '🥚', eggs: '🥚', lemon: '🍋', milk: '🥛', onion: '🧅', orange: '🍊', oranges: '🍊', pasta: '🍝', potato: '🥔', potatoes: '🥔', rice: '🍚', spinach: '🥬', tomato: '🍅', tomatoes: '🍅', yogurt: '🥣'
  };
  const categories = [
    { id: 'produce', label: 'Fruit & veg' },
    { id: 'dairy', label: 'Dairy & eggs' },
    { id: 'bakery', label: 'Bakery' },
    { id: 'pantry', label: 'Pantry staples' },
    { id: 'leftovers', label: 'Leftovers' },
    { id: 'other', label: 'Other' }
  ];
  const suggestions = {
    bread: 'Toast it, make a quick sandwich, or freeze slices for later.',
    banana: 'Slice it onto oats, blend into a smoothie, or freeze for later.',
    spinach: 'Stir a handful into pasta, eggs, soup, or a quick rice bowl.',
    tomato: 'Add it to toast, a simple salad, or a quick pan sauce.',
    tomatoes: 'Add them to toast, a simple salad, or a quick pan sauce.',
    carrot: 'Grate into noodles, add to a soup, or roast with what you have.',
    carrots: 'Grate into noodles, add to a soup, or roast with what you have.',
    rice: 'Try a quick fried-rice style meal with vegetables you already have.',
    pasta: 'Toss with vegetables and a little oil for an easy leftover bowl.',
    cheese: 'Add a little to toast, eggs, or a warm vegetable dish.'
  };
  const demoShares = [
    { id: 'demo-1', name: 'A few ripe bananas', note: 'Common kitchen · collect by 6 pm', emoji: '🍌', owner: 'Maya', demo: true },
    { id: 'demo-2', name: 'Extra pasta (sealed)', note: 'Hall B lounge · this evening', emoji: '🍝', owner: 'Nimal', demo: true },
    { id: 'demo-3', name: 'Fresh garden tomatoes', note: 'Library entrance · message first', emoji: '🍅', owner: 'Asha', demo: true }
  ];

  const $ = (selector) => document.querySelector(selector);
  const foodList = $('#food-list');
  const shareList = $('#share-list');
  const roomList = $('#room-list');
  const messageList = $('#message-list');
  const foodDialog = $('#food-dialog');
  const shareDialog = $('#share-dialog');
  const roomDialog = $('#room-dialog');
  const foodForm = $('#food-form');
  const shareForm = $('#share-form');
  const roomForm = $('#room-form');
  const toast = $('#toast');
  let activeView = 'home';
  let activeCategory = 'all';
  let timingFilter = 'all';
  let activeRoomId = null;
  let toastTimer;
  let undoSnapshot = null;

  function todayAtNoon() {
    const date = new Date();
    date.setHours(12, 0, 0, 0);
    return date;
  }

  function dateOffset(days) {
    const date = todayAtNoon();
    date.setDate(date.getDate() + days);
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
  }

  function sampleRooms() {
    return [
      {
        id: 'room-flat-3', name: 'Flat 3 kitchen', members: ['You', 'Maya', 'Nimal'], unread: 1,
        messages: [
          { from: 'Maya', text: 'I have extra tomatoes if anyone wants some 🍅', time: '10:42' },
          { from: 'You', text: 'I can use a few for lunch!', time: '10:46' },
          { from: 'Nimal', text: 'I’ll bring bread home too.', time: '11:03' }
        ]
      },
      {
        id: 'room-meal-prep', name: 'Meal prep crew', members: ['You', 'Asha', 'Ravi'], unread: 0,
        messages: [
          { from: 'Asha', text: 'Soup night? I have carrots and lentils.', time: 'Yesterday' },
          { from: 'Ravi', text: 'Sounds good. I can bring rice.', time: 'Yesterday' }
        ]
      }
    ];
  }

  function starterState() {
    return {
      items: [
        { id: 'seed-avocado', name: 'Avocado', quantity: '2 pieces', date: dateOffset(1), shared: false, category: 'produce' },
        { id: 'seed-spinach', name: 'Spinach', quantity: '1 small bag', date: dateOffset(2), shared: false, category: 'produce' },
        { id: 'seed-bread', name: 'Sourdough bread', quantity: 'Half a loaf', date: dateOffset(5), shared: false, category: 'bakery' },
        { id: 'seed-yogurt', name: 'Plain yogurt', quantity: '1 tub', date: dateOffset(4), shared: false, category: 'dairy' },
        { id: 'seed-tomato', name: 'Cherry tomatoes', quantity: '1 punnet', date: dateOffset(0), shared: false, category: 'produce' },
        { id: 'seed-rice', name: 'Cooked rice', quantity: '1 container', date: dateOffset(1), shared: false, category: 'leftovers' }
      ],
      shares: [],
      claimed: [],
      rooms: sampleRooms()
    };
  }

  function categoryForName(name) {
    const key = String(name).toLocaleLowerCase().trim();
    if (/leftover|cooked|prepared/.test(key)) return 'leftovers';
    if (/milk|cheese|egg|yogurt|yoghurt|butter|cream/.test(key)) return 'dairy';
    if (/bread|bagel|bun|roll|tortilla|muffin|pastry/.test(key)) return 'bakery';
    if (/pasta|rice|oat|flour|bean|lentil|cereal|oil|sauce|can|tin|noodle/.test(key)) return 'pantry';
    if (/apple|avocado|banana|berry|berries|carrot|lemon|lime|onion|orange|pear|potato|spinach|tomato|lettuce|pepper|cucumber|fruit|vegetable|broccoli|garlic/.test(key)) return 'produce';
    return 'other';
  }

  function normalizeItem(item) {
    return { ...item, category: categories.some((category) => category.id === item.category) ? item.category : categoryForName(item.name) };
  }

  function categoryGlyph(id) {
    const paths = {
      all: '<circle cx="12" cy="12" r="8.5"></circle><path d="M12 7v10M7 12h10"></path>',
      produce: '<path d="M20 4C11 4 5 8 5 14c0 3.4 2.4 5.5 5.6 5.5C16.5 19.5 20 12.5 20 4Z"></path><path d="M4 21 15 9"></path>',
      dairy: '<path d="M8 4h8l2 3v13H6V7l2-3Z"></path><path d="M8 4v5h8V4M7 13h10"></path>',
      bakery: '<path d="M4 11c0-3.9 3.6-7 8-7s8 3.1 8 7v8H4v-8Z"></path><path d="M9 9v3m6-3v3M4 15h16"></path>',
      pantry: '<path d="M6 5h12v15H6zM8 5V3h8v2M6 9h12M10 12h4"></path>',
      leftovers: '<path d="M4 12h16a8 8 0 0 1-16 0Z"></path><path d="M3 12h18M8 8l-1-2m5 2V5m5 3 1-2"></path>',
      other: '<path d="M4 10h16l-1.5 10h-13L4 10Z"></path><path d="m4 10 2-5h12l2 5M8 10v10m8-10v10M2.5 10h19"></path>'
    };
    return `<svg viewBox="0 0 24 24" aria-hidden="true">${paths[id] || paths.other}</svg>`;
  }

  function loadState() {
    try {
      const saved = JSON.parse(localStorage.getItem(STORAGE_KEY));
      if (saved && Array.isArray(saved.items) && Array.isArray(saved.shares) && Array.isArray(saved.claimed)) {
        return {
          items: saved.items.map(normalizeItem),
          shares: saved.shares,
          claimed: saved.claimed,
          rooms: Array.isArray(saved.rooms) ? saved.rooms : sampleRooms()
        };
      }
    } catch (error) {
      // Invalid or unavailable storage falls back to a fresh local demo.
    }
    return starterState();
  }

  let state = loadState();

  function saveState() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (error) {
      showToast('Changes are saved while this page stays open.');
    }
  }

  function escapeHTML(value) {
    return String(value).replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[character]);
  }

  function emojiFor(name) {
    const key = String(name).toLocaleLowerCase().match(/[a-z]+/)?.[0] || '';
    return foodEmojis[key] || '🥬';
  }

  function dayDistance(dateString) {
    if (!dateString) return null;
    const target = new Date(`${dateString}T12:00:00`);
    if (Number.isNaN(target.getTime())) return null;
    return Math.round((target.getTime() - todayAtNoon().getTime()) / DAY_MS);
  }

  function dateLabel(dateString) {
    const days = dayDistance(dateString);
    if (days === null) return 'No reminder date';
    if (days < 0) return 'Reminder date passed';
    if (days === 0) return 'Use today';
    if (days === 1) return 'Use tomorrow';
    if (days <= 3) return `Use in ${days} days`;
    return `Use by ${new Intl.DateTimeFormat(undefined, { month: 'short', day: 'numeric' }).format(new Date(`${dateString}T12:00:00`))}`;
  }

  function isSoon(item) {
    const days = dayDistance(item.date);
    return days !== null && days >= 0 && days <= 2;
  }

  function showToast(message, canUndo = false) {
    toast.replaceChildren();
    const label = document.createElement('span');
    label.className = 'toast-message';
    label.textContent = message;
    toast.append(label);
    if (canUndo && undoSnapshot) {
      const undo = document.createElement('button');
      undo.type = 'button';
      undo.className = 'toast-undo';
      undo.textContent = 'Undo';
      undo.addEventListener('click', () => {
        state = undoSnapshot;
        undoSnapshot = null;
        saveState();
        render();
        window.clearTimeout(toastTimer);
        toast.classList.remove('visible');
        showToast('Change undone.');
      });
      toast.append(undo);
    }
    toast.classList.add('visible');
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(() => toast.classList.remove('visible'), 3000);
  }

  function rememberForUndo() {
    undoSnapshot = JSON.parse(JSON.stringify(state));
  }

  function setView(view) {
    activeView = view;
    document.querySelectorAll('[data-screen]').forEach((screen) => {
      const isActive = screen.dataset.screen === view;
      screen.hidden = !isActive;
      screen.classList.toggle('active-screen', isActive);
    });
    document.querySelectorAll('.nav-item').forEach((button) => {
      const isActive = button.dataset.nav === view;
      button.classList.toggle('active', isActive);
      if (isActive) button.setAttribute('aria-current', 'page');
      else button.removeAttribute('aria-current');
    });
    if (view === 'chats' && activeRoomId) showRoomDetail();
    else if (view === 'chats') showRoomList();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function renderCategories() {
    const counts = Object.fromEntries(categories.map((category) => [category.id, state.items.filter((item) => item.category === category.id).length]));
    const allButton = `<button class="category-chip ${activeCategory === 'all' ? 'active' : ''}" type="button" data-category="all" aria-pressed="${activeCategory === 'all'}"><span class="category-icon">${categoryGlyph('all')}</span><span>All</span><small>${state.items.length}</small></button>`;
    const categoryButtons = categories.map((category) => `<button class="category-chip ${activeCategory === category.id ? 'active' : ''}" type="button" data-category="${category.id}" aria-pressed="${activeCategory === category.id}"><span class="category-icon">${categoryGlyph(category.id)}</span><span>${escapeHTML(category.label)}</span><small>${counts[category.id]}</small></button>`).join('');
    $('#category-filters').innerHTML = allButton + categoryButtons;
  }

  function renderFood() {
    renderCategories();
    const visible = state.items.filter((item) => {
      if (activeCategory !== 'all' && item.category !== activeCategory) return false;
      if (timingFilter === 'soon' && !isSoon(item)) return false;
      return true;
    });
    const soonCount = state.items.filter(isSoon).length;
    $('#hero-count').textContent = String(state.items.length);
    $('#soon-count').textContent = String(soonCount);
    $('#all-count').textContent = String(state.items.length);
    $('#filter-soon-count').textContent = String(soonCount);
    $('#empty-state').hidden = visible.length !== 0;
    foodList.hidden = visible.length === 0;
    if (visible.length === 0) {
      const emptyCopy = timingFilter === 'soon'
        ? ['Nothing needs a reminder soon.', 'Items due today or within 2 days will show up here.']
        : activeCategory === 'all'
          ? ['Your pantry has room to grow.', 'Add a food item and we’ll help you remember it.']
          : [`No ${categories.find((category) => category.id === activeCategory)?.label.toLocaleLowerCase() || 'food'} yet.`, 'Add an item to see it in this category.'];
      $('#empty-title').textContent = emptyCopy[0];
      $('#empty-copy').textContent = emptyCopy[1];
    }
    foodList.innerHTML = visible.map((item) => {
      const days = dayDistance(item.date);
      const overdue = days !== null && days < 0;
      const category = categories.find((entry) => entry.id === item.category) || categories.at(-1);
      const reminderClass = isSoon(item) || overdue ? 'reminder-soon' : '';
      return `<article class="food-row" data-id="${escapeHTML(item.id)}">
        <span class="food-emoji" aria-hidden="true">${emojiFor(item.name)}</span>
        <div class="food-details"><div class="food-name-line"><h2>${escapeHTML(item.name)}</h2><span class="item-category">${categoryGlyph(category.id)} ${escapeHTML(category.label)}</span></div><p>${escapeHTML(item.quantity || 'Added to your pantry')}</p><span class="food-date ${reminderClass}">${escapeHTML(dateLabel(item.date))}</span></div>
        <div class="food-row-actions"><button class="food-more" type="button" data-action="more" data-id="${escapeHTML(item.id)}" aria-label="More actions for ${escapeHTML(item.name)}" aria-expanded="false" aria-controls="food-menu-${escapeHTML(item.id)}"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="5" cy="12" r="1.2"></circle><circle cx="12" cy="12" r="1.2"></circle><circle cx="19" cy="12" r="1.2"></circle></svg></button><button class="food-idea" type="button" data-action="idea" data-id="${escapeHTML(item.id)}">Idea <span aria-hidden="true">→</span></button></div>
        <div id="food-menu-${escapeHTML(item.id)}" class="food-action-menu" hidden><button type="button" data-action="share" data-id="${escapeHTML(item.id)}">${item.shared ? 'Already shared' : 'Share extra'}</button><button type="button" data-action="used" data-id="${escapeHTML(item.id)}">Mark used</button>${item.shared ? '<button type="button" data-action="unshare" data-id="' + escapeHTML(item.id) + '">Remove from share board</button>' : ''}<button type="button" data-action="remove" data-id="${escapeHTML(item.id)}">Remove from pantry</button></div>
      </article>`;
    }).join('');

    const next = [...state.items].filter((item) => item.date).sort((a, b) => String(a.date).localeCompare(String(b.date)))[0];
    $('#leftover-prompt').textContent = next
      ? (suggestions[next.name.toLocaleLowerCase()] || `Could ${next.name.toLocaleLowerCase()} work in a quick bowl, toast, or simple side? Start with what you already have.`)
      : 'Add something to your pantry and we’ll help you think of a simple next step.';
    renderHomeSoon();
  }

  function renderHomeSoon() {
    const soon = [...state.items].filter(isSoon).sort((a, b) => String(a.date).localeCompare(String(b.date))).slice(0, 3);
    const container = $('#home-soon-list');
    if (!soon.length) {
      container.innerHTML = '<div class="calm-empty"><span aria-hidden="true">✓</span><p>Nothing needs a reminder soon.</p></div>';
      return;
    }
    container.innerHTML = soon.map((item) => `<button class="mini-food" type="button" data-go="pantry"><span class="mini-food-icon" aria-hidden="true">${emojiFor(item.name)}</span><span class="mini-food-copy"><strong>${escapeHTML(item.name)}</strong><small>${escapeHTML(item.quantity || categories.find((category) => category.id === item.category)?.label || 'On your shelf')}</small></span><span class="mini-date">${escapeHTML(dateLabel(item.date))}</span></button>`).join('');
  }

  function renderShares() {
    const claimed = new Set(state.claimed);
    const listings = [...state.shares.filter((item) => !claimed.has(item.id)), ...demoShares.filter((item) => !claimed.has(item.id))];
    if (listings.length === 0) {
      shareList.innerHTML = '<div class="calm-empty"><span aria-hidden="true">✦</span><p>The board is quiet for now. Add an example offer to see the preview.</p></div>';
      return;
    }
    shareList.innerHTML = listings.map((item) => `<article class="share-row"><span class="share-emoji" aria-hidden="true">${escapeHTML(item.emoji || emojiFor(item.name))}</span><div class="share-info"><h2>${escapeHTML(item.name)}</h2><p>From ${escapeHTML(item.owner || 'a friend')}${item.demo ? ' · sample' : ' · your preview'}</p><p class="pickup">${escapeHTML(item.note || 'Pickup details to be agreed')}</p></div><button class="share-claim" type="button" data-claim="${escapeHTML(item.id)}">Interested</button></article>`).join('');
  }

  function initials(name) {
    const words = String(name).trim().split(/\s+/);
    return words.length > 1 ? `${words[0][0]}${words[1][0]}`.toUpperCase() : String(name).slice(0, 1).toUpperCase();
  }

  function lastMessage(room) {
    return room.messages?.[room.messages.length - 1];
  }

  function renderRoomList() {
    if (!state.rooms.length) {
      roomList.innerHTML = '<div class="calm-empty"><span aria-hidden="true">☏</span><p>No rooms yet. Start one with friends.</p></div>';
      return;
    }
    roomList.innerHTML = state.rooms.map((room, index) => {
      const last = lastMessage(room);
      return `<button class="room-row" type="button" data-room="${escapeHTML(room.id)}"><span class="room-avatar room-color-${index % 4}" aria-hidden="true">${initials(room.name)}</span><span class="room-preview"><strong>${escapeHTML(room.name)}</strong><small>${escapeHTML(last ? `${last.from === 'You' ? 'You: ' : `${last.from}: `}${last.text}` : `${room.members.length - 1} friends · Start the conversation`)}</small></span><span class="room-side"><small>${escapeHTML(last?.time || '')}</small>${room.unread ? `<span class="unread-badge">${room.unread}</span>` : ''}</span></button>`;
    }).join('');
  }

  function renderHomeChats() {
    const container = $('#home-chat-list');
    container.innerHTML = state.rooms.slice(0, 2).map((room, index) => {
      const last = lastMessage(room);
      return `<button class="home-chat-row" type="button" data-room="${escapeHTML(room.id)}"><span class="room-avatar room-color-${index % 4}" aria-hidden="true">${initials(room.name)}</span><span><strong>${escapeHTML(room.name)}</strong><small>${escapeHTML(last ? `${last.from === 'You' ? 'You: ' : ''}${last.text}` : 'Start the conversation')}</small></span><span class="home-chat-arrow" aria-hidden="true">→</span></button>`;
    }).join('') || '<div class="calm-empty"><p>Create a room to start chatting with friends.</p></div>';
  }

  function formatMemberCount(room) {
    const friends = room.members.filter((member) => member !== 'You').length;
    return `${friends} ${friends === 1 ? 'friend' : 'friends'} · ${room.members.length} ${room.members.length === 1 ? 'member' : 'members'}`;
  }

  function renderMessages(room) {
    $('#active-room-title').textContent = room.name;
    $('#active-room-members').textContent = formatMemberCount(room);
    $('#member-pills').innerHTML = room.members.map((member, index) => `<span class="member-pill"><span class="member-avatar member-color-${index % 4}" aria-hidden="true">${initials(member)}</span>${escapeHTML(member)}</span>`).join('');
    const messages = room.messages || [];
    if (!messages.length) {
      messageList.innerHTML = '<div class="chat-welcome"><span aria-hidden="true">✳</span><strong>Your room is ready.</strong><p>Say hi and get the conversation started.</p></div>';
      return;
    }
    messageList.innerHTML = messages.map((message) => {
      const own = message.from === 'You';
      return `<div class="message-line ${own ? 'message-own' : ''}">${own ? '' : `<span class="message-avatar" aria-hidden="true">${initials(message.from)}</span>`}<div class="message-stack">${own ? '' : `<span class="message-author">${escapeHTML(message.from)}</span>`}<div class="message-bubble">${escapeHTML(message.text)}</div><span class="message-time">${escapeHTML(message.time || '')}</span></div></div>`;
    }).join('');
    messageList.scrollTop = messageList.scrollHeight;
  }

  function showRoomList() {
    $('#room-list-view').hidden = false;
    $('#chat-detail-view').hidden = true;
    renderRoomList();
  }

  function showRoomDetail() {
    const room = state.rooms.find((entry) => entry.id === activeRoomId);
    if (!room) {
      activeRoomId = null;
      showRoomList();
      return;
    }
    if (room.unread) {
      room.unread = 0;
      saveState();
    }
    $('#room-list-view').hidden = true;
    $('#chat-detail-view').hidden = false;
    $('#member-form-wrap').hidden = true;
    $('#add-member-open').setAttribute('aria-expanded', 'false');
    renderMessages(room);
    renderChatCount();
  }

  function renderChatCount() {
    const count = state.rooms.reduce((total, room) => total + Number(room.unread || 0), 0);
    const badge = $('#chat-count');
    badge.hidden = count === 0;
    badge.textContent = String(count);
  }

  function render() {
    renderFood();
    renderShares();
    renderRoomList();
    renderHomeChats();
    renderChatCount();
    if (activeRoomId && activeView === 'chats') {
      const room = state.rooms.find((entry) => entry.id === activeRoomId);
      if (room) renderMessages(room);
      else {
        activeRoomId = null;
        showRoomList();
      }
    }
  }

  function openRoom(roomId) {
    activeRoomId = roomId;
    setView('chats');
  }

  function openFoodDialog() {
    foodForm.reset();
    $('#food-date').min = dateOffset(0);
    foodDialog.showModal();
    $('#food-name').focus();
  }

  function openShareDialog() {
    shareForm.reset();
    shareDialog.showModal();
    $('#share-name').focus();
  }

  function openRoomDialog() {
    roomForm.reset();
    roomDialog.showModal();
    $('#room-name').focus();
  }

  document.querySelectorAll('[data-nav], [data-go]').forEach((button) => {
    button.addEventListener('click', (event) => {
      const view = event.currentTarget.dataset.nav || event.currentTarget.dataset.go;
      if (view) setView(view);
    });
  });
  $('#open-form').addEventListener('click', openFoodDialog);
  $('#empty-add').addEventListener('click', openFoodDialog);
  document.querySelector('[data-action="open-food"]').addEventListener('click', openFoodDialog);
  $('#share-open').addEventListener('click', openShareDialog);
  $('#new-room-open').addEventListener('click', openRoomDialog);
  document.querySelector('[data-action="new-room"]').addEventListener('click', openRoomDialog);
  document.querySelector('[data-action="open-share"]').addEventListener('click', openShareDialog);
  $('#chat-back').addEventListener('click', () => {
    activeRoomId = null;
    showRoomList();
  });
  $('#add-member-open').addEventListener('click', () => {
    const form = $('#member-form-wrap');
    form.hidden = !form.hidden;
    $('#add-member-open').setAttribute('aria-expanded', String(!form.hidden));
    if (!form.hidden) $('#member-name').focus();
  });
  document.querySelectorAll('[data-close]').forEach((button) => {
    button.addEventListener('click', () => document.getElementById(button.dataset.close).close());
  });

  foodForm.addEventListener('submit', (event) => {
    event.preventDefault();
    const data = new FormData(foodForm);
    const name = String(data.get('name') || '').trim();
    if (!name) return $('#food-name').focus();
    rememberForUndo();
    const category = String(data.get('category') || 'auto');
    state.items.unshift({
      id: `food-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
      name,
      quantity: String(data.get('quantity') || '').trim(),
      date: String(data.get('date') || ''),
      shared: false,
      category: category === 'auto' ? categoryForName(name) : category
    });
    saveState();
    render();
    foodDialog.close();
    showToast(`${name} added to your pantry.`, true);
  });

  shareForm.addEventListener('submit', (event) => {
    event.preventDefault();
    const data = new FormData(shareForm);
    const name = String(data.get('name') || '').trim();
    if (!name) return $('#share-name').focus();
    rememberForUndo();
    state.shares.unshift({ id: `share-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`, name, note: String(data.get('note') || '').trim(), emoji: emojiFor(name), owner: 'You', demo: false });
    saveState();
    render();
    shareDialog.close();
    showToast('Offer preview added on this device. No one was contacted.', true);
  });

  roomForm.addEventListener('submit', (event) => {
    event.preventDefault();
    const data = new FormData(roomForm);
    const name = String(data.get('name') || '').trim();
    if (!name) return $('#room-name').focus();
    const friends = String(data.get('friends') || '').split(/[\n,]/).map((friend) => friend.trim()).filter(Boolean);
    if (!friends.length) return $('#room-friends').focus();
    const members = ['You'];
    friends.forEach((friend) => {
      const alreadyAdded = members.some((member) => member.toLocaleLowerCase() === friend.toLocaleLowerCase());
      if (!alreadyAdded) members.push(friend);
    });
    const room = { id: `room-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`, name, members, unread: 0, messages: [] };
    state.rooms.unshift(room);
    saveState();
    render();
    roomDialog.close();
    activeRoomId = room.id;
    setView('chats');
    showToast(`${name} is ready. This demo doesn’t send invitations.`);
  });

  $('#member-form').addEventListener('submit', (event) => {
    event.preventDefault();
    const room = state.rooms.find((entry) => entry.id === activeRoomId);
    const name = String(new FormData(event.currentTarget).get('member') || '').trim();
    if (!room || !name) return;
    if (room.members.some((member) => member.toLocaleLowerCase() === name.toLocaleLowerCase())) {
      showToast(`${name} is already in this room.`);
      return;
    }
    room.members.push(name);
    saveState();
    renderMessages(room);
    event.currentTarget.reset();
    $('#member-form-wrap').hidden = true;
    $('#add-member-open').setAttribute('aria-expanded', 'false');
    showToast(`${name} added to this local room.`);
  });

  $('#message-form').addEventListener('submit', (event) => {
    event.preventDefault();
    const room = state.rooms.find((entry) => entry.id === activeRoomId);
    const input = $('#message-text');
    const text = input.value.trim();
    if (!room || !text) return;
    const now = new Intl.DateTimeFormat(undefined, { hour: 'numeric', minute: '2-digit' }).format(new Date());
    room.messages.push({ from: 'You', text, time: now });
    saveState();
    renderMessages(room);
    renderRoomList();
    renderHomeChats();
    input.value = '';
    input.focus();
  });

  foodList.addEventListener('click', (event) => {
    const button = event.target.closest('button[data-action]');
    if (!button) return;
    const item = state.items.find((entry) => entry.id === button.dataset.id);
    if (!item && button.dataset.action !== 'more') return;
    if (button.dataset.action === 'more') {
      const menu = button.closest('.food-row').querySelector('.food-action-menu');
      const wasHidden = menu.hidden;
      foodList.querySelectorAll('.food-action-menu').forEach((entry) => {
        entry.hidden = true;
        entry.parentElement.querySelector('.food-more').setAttribute('aria-expanded', 'false');
      });
      menu.hidden = !wasHidden;
      button.setAttribute('aria-expanded', String(!wasHidden));
      return;
    }
    if (button.dataset.action === 'idea') {
      $('#leftover-prompt').textContent = suggestions[item.name.toLocaleLowerCase()] || `Could ${item.name.toLocaleLowerCase()} work in a quick bowl, toast, or simple side? Start with what you already have.`;
      showToast('A leftover idea is ready in your pantry.');
      return;
    }
    rememberForUndo();
    let message = '';
    switch (button.dataset.action) {
      case 'remove':
        state.items = state.items.filter((entry) => entry.id !== item.id);
        message = `${item.name} removed from your pantry.`;
        break;
      case 'used':
        state.items = state.items.filter((entry) => entry.id !== item.id);
        message = `Nice work using ${item.name}.`;
        break;
      case 'share':
        if (item.shared) return showToast(`${item.name} is already on your share board.`);
        item.shared = true;
        state.shares.unshift({ id: `share-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`, sourceItemId: item.id, name: item.name, note: `Offer from your pantry · ${item.quantity || 'quantity to agree'}`, emoji: emojiFor(item.name), owner: 'You', demo: false });
        message = `${item.name} added to your local share board.`;
        break;
      case 'unshare':
        item.shared = false;
        state.shares = state.shares.filter((entry) => entry.sourceItemId !== item.id);
        message = `${item.name} removed from the local board.`;
        break;
      default:
        return;
    }
    saveState();
    render();
    showToast(message, true);
  });

  $('#category-filters').addEventListener('click', (event) => {
    const button = event.target.closest('[data-category]');
    if (!button) return;
    activeCategory = button.dataset.category;
    renderFood();
  });

  document.querySelectorAll('[data-timing]').forEach((button) => {
    button.addEventListener('click', () => {
      timingFilter = button.dataset.timing;
      document.querySelectorAll('[data-timing]').forEach((filter) => {
        const selected = filter === button;
        filter.classList.toggle('active', selected);
        filter.setAttribute('aria-pressed', String(selected));
      });
      renderFood();
    });
  });

  roomList.addEventListener('click', (event) => {
    const button = event.target.closest('[data-room]');
    if (button) openRoom(button.dataset.room);
  });
  $('#home-chat-list').addEventListener('click', (event) => {
    const button = event.target.closest('[data-room]');
    if (button) openRoom(button.dataset.room);
  });

  shareList.addEventListener('click', (event) => {
    const button = event.target.closest('button[data-claim]');
    if (!button) return;
    const listing = [...state.shares, ...demoShares].find((entry) => entry.id === button.dataset.claim);
    if (!listing) return;
    rememberForUndo();
    state.claimed.push(listing.id);
    saveState();
    renderShares();
    showToast('Interest previewed. No one was contacted.', true);
  });

  window.addEventListener('storage', (event) => {
    if (event.key === STORAGE_KEY) {
      state = loadState();
      render();
    }
  });

  render();
})();
