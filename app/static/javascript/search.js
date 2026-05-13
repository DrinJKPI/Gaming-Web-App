/**
 * Game Search and Filter System
 * Implements real-time search with multiple filter options for games within the dtatabase
 */

// Wait for DOM to be fully loaded

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const gameCards = document.querySelectorAll('.game-card');
    const searchInput = document.getElementById('searchInput');
    const searchDropdown = document.getElementById('searchDropdown');
    const toggleBtn = document.getElementById('toggleFilters');
    const filterPanel = document.getElementById('filterCollapse');
    const clearFiltersBtn = document.getElementById('clearFilters');
    const visibleCountEl = document.getElementById('visibleCount');
    const totalCountEl = document.getElementById('totalCount');
    const noResultsEl = document.getElementById('noResults');

    // Initial counts
    totalCountEl.textContent = gameCards.length;
    visibleCountEl.textContent = gameCards.length;

    // --- Dynamic Filter Population ---
    const genres = new Set();
    const platforms = new Set();

    gameCards.forEach(card => {
        const cardGenres = card.dataset.genres.split(',').filter(g => g.trim());
        cardGenres.forEach(genre => genres.add(genre.trim()));
        const cardPlatform = card.dataset.platform.trim();
        if (cardPlatform) platforms.add(cardPlatform);
    });

    const genreFiltersContainer = document.getElementById('genreFilters');
    Array.from(genres).sort().forEach(genre => {
        const label = document.createElement('label');
        label.innerHTML = `<input type="checkbox" class="genre-filter" value="${genre}"> ${genre.charAt(0).toUpperCase() + genre.slice(1)}`;
        genreFiltersContainer.appendChild(label);
    });

    const platformFiltersContainer = document.getElementById('platformFilters');
    Array.from(platforms).sort().forEach(platform => {
        const label = document.createElement('label');
        label.innerHTML = `<input type="checkbox" class="platform-filter" value="${platform}"> ${platform.charAt(0).toUpperCase() + platform.slice(1)}`;
        platformFiltersContainer.appendChild(label);
    });

    const genreCheckboxes = document.querySelectorAll('.genre-filter');
    const platformCheckboxes = document.querySelectorAll('.platform-filter');
    const priceCheckboxes = document.querySelectorAll('.price-filter');

    // --- Core Filter Function ---
    function applyFilters() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        const searchTokens = searchTerm.split(/\s+/).filter(t => t.length > 0);
        
        const selectedGenres = Array.from(genreCheckboxes).filter(cb => cb.checked).map(cb => cb.value);
        const selectedPlatforms = Array.from(platformCheckboxes).filter(cb => cb.checked).map(cb => cb.value);
        const selectedPriceRanges = Array.from(priceCheckboxes).filter(cb => cb.checked).map(cb => cb.value);

        let visibleCount = 0;

        gameCards.forEach(card => {
            const title = (card.dataset.title || '').toLowerCase();
            const cardGenres = (card.dataset.genres || '').split(',').map(g => g.trim());
            const platform = card.dataset.platform;
            const price = parseFloat(card.dataset.price);

            // Token-based matching: ALL search words must be in the title
            const matchesSearch = searchTokens.every(token => title.includes(token));
            const matchesGenre = selectedGenres.length === 0 || selectedGenres.some(g => cardGenres.includes(g));
            const matchesPlatform = selectedPlatforms.length === 0 || selectedPlatforms.includes(platform);
            const matchesPrice = selectedPriceRanges.length === 0 || selectedPriceRanges.some(range => isPriceInRange(price, range));

            if (matchesSearch && matchesGenre && matchesPlatform && matchesPrice) {
                card.style.display = 'block';
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });

        visibleCountEl.textContent = visibleCount;
        noResultsEl.style.display = visibleCount === 0 ? 'block' : 'none';
    }

    function isPriceInRange(price, range) {
        if (range === 'free') return price === 0;
        if (range === '0-20') return price > 0 && price <= 20;
        if (range === '20-40') return price > 20 && price <= 40;
        if (range === '40-60') return price > 40 && price <= 60;
        if (range === '60+') return price > 60;
        return false;
    }

    // --- Dropdown API Logic ---
    async function updateDropdown() {
        const query = searchInput.value.trim();
        if (query.length < 2) {
            searchDropdown.style.display = 'none';
            return;
        }

        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            const results = await response.json();

            if (results.length > 0) {
                searchDropdown.innerHTML = results.map(game => `
                    <div class="dropdown-item-custom" onclick="window.location.href='/game/${game.game_id}'">
                        <img src="${game.image || '/static/images/default_game.jpg'}" alt="">
                        <div class="game-info">
                            <span class="title">${game.title}</span>
                            <span class="category">${game.platform}</span>
                        </div>
                        <span class="price-tag">$${parseFloat(game.price).toFixed(2)}</span>
                    </div>
                `).join('');
                searchDropdown.style.display = 'block';
            } else {
                searchDropdown.style.display = 'none';
            }
        } catch (err) { console.error("Search API Error", err); }
    }

    // --- Helpers ---
    function debounce(func, wait) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }

    // --- Listeners ---
    if (toggleBtn && filterPanel) {
        toggleBtn.addEventListener('click', () => {
            filterPanel.classList.toggle('active');
            toggleBtn.textContent = filterPanel.classList.contains('active') ? 'Hide Filters' : 'Filters';
        });
    }

    if (searchInput) {
        searchInput.addEventListener('input', debounce(() => {
            applyFilters();
            if (typeof updateDropdown === 'function') updateDropdown();
        }, 300));
    }

    [...genreCheckboxes, ...platformCheckboxes, ...priceCheckboxes].forEach(cb => {
        cb.addEventListener('change', applyFilters);
    });

    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', () => {
            if (searchInput) searchInput.value = '';
            [...genreCheckboxes, ...platformCheckboxes, ...priceCheckboxes].forEach(cb => cb.checked = false);
            applyFilters();
        });
    }

    document.addEventListener('click', (e) => {
        if (searchInput && searchDropdown) {
            if (!searchInput.contains(e.target) && !searchDropdown.contains(e.target)) {
                searchDropdown.style.display = 'none';
            }
        }
    });

    applyFilters();
});