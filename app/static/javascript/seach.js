/**
 * Game Search and Filter System
 * Implements real-time search with multiple filter options for games within the dtatabase
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {

    // Get all game cards
    const gameCards = document.querySelectorAll('.game-card');
    const searchInput = document.getElementById('searchInput');
    const clearFiltersBtn = document.getElementById('clearFilters');
    const visibleCountEl = document.getElementById('visibleCount');
    const totalCountEl = document.getElementById('totalCount');
    const noResultsEl = document.getElementById('noResults');

    // Set total count
    totalCountEl.textContent = gameCards.length;
    visibleCountEl.textContent = gameCards.length;

    // Extract unique genres and platforms from games
    const genres = new Set();
    const platforms = new Set();

    gameCards.forEach(card => {
        const cardGenres = card.dataset.genres.split(',').filter(g => g.trim());
        cardGenres.forEach(genre => genres.add(genre.trim()));

        const cardPlatform = card.dataset.platform.trim();
        if (cardPlatform) platforms.add(cardPlatform);
    });

    // Populate Genre Filters
    const genreFiltersContainer = document.getElementById('genreFilters');
    Array.from(genres).sort().forEach(genre => {
        const label = document.createElement('label');
        label.innerHTML = `
            <input type="checkbox" class="genre-filter" value="${genre}">
            ${capitalizeFirst(genre)}
        `;
        genreFiltersContainer.appendChild(label);
    });

    // Populate Platform Filters
    const platformFiltersContainer = document.getElementById('platformFilters');
    Array.from(platforms).sort().forEach(platform => {
        const label = document.createElement('label');
        label.innerHTML = `
            <input type="checkbox" class="platform-filter" value="${platform}">
            ${capitalizeFirst(platform)}
        `;
        platformFiltersContainer.appendChild(label);
    });

    // Get filter elements
    const genreCheckboxes = document.querySelectorAll('.genre-filter');
    const platformCheckboxes = document.querySelectorAll('.platform-filter');
    const priceCheckboxes = document.querySelectorAll('.price-filter');

    /**
     * Main filter function - applies all active filters
     */
    function applyFilters() {
        const searchTerm = searchInput.value.toLowerCase().trim();

        // Get selected filters
        const selectedGenres = Array.from(genreCheckboxes)
            .filter(cb => cb.checked)
            .map(cb => cb.value);

        const selectedPlatforms = Array.from(platformCheckboxes)
            .filter(cb => cb.checked)
            .map(cb => cb.value);

        const selectedPriceRanges = Array.from(priceCheckboxes)
            .filter(cb => cb.checked)
            .map(cb => cb.value);

        let visibleCount = 0;

        // Filter each game card
        gameCards.forEach(card => {
            const title = card.dataset.title;
            const cardGenres = card.dataset.genres.split(',').map(g => g.trim());
            const platform = card.dataset.platform;
            const price = parseFloat(card.dataset.price);

            // Check text search
            const matchesSearch = title.includes(searchTerm);

            // Check genre filter (OR logic - match any selected genre)
            const matchesGenre = selectedGenres.length === 0 ||
                selectedGenres.some(genre => cardGenres.includes(genre));

            // Check platform filter
            const matchesPlatform = selectedPlatforms.length === 0 ||
                selectedPlatforms.includes(platform);

            // Check price filter
            const matchesPrice = selectedPriceRanges.length === 0 ||
                selectedPriceRanges.some(range => isPriceInRange(price, range));

            // Show card only if ALL filters match
            if (matchesSearch && matchesGenre && matchesPlatform && matchesPrice) {
                card.classList.remove('hidden');
                visibleCount++;
            } else {
                card.classList.add('hidden');
            }
        });

        // Update results count
        visibleCountEl.textContent = visibleCount;

        // Show/hide "no results" message
        if (visibleCount === 0) {
            noResultsEl.style.display = 'block';
        } else {
            noResultsEl.style.display = 'none';
        }
    }

    /**
     * Check if price falls within a range
     */
    function isPriceInRange(price, range) {
        if (range === 'free') return price === 0;
        if (range === '0-20') return price > 0 && price <= 20;
        if (range === '20-40') return price > 20 && price <= 40;
        if (range === '40-60') return price > 40 && price <= 60;
        if (range === '60+') return price > 60;
        return false;
    }

    /**
     * Debounce function to limit search frequency
     */
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * Clear all filters
     */
    function clearAllFilters() {
        searchInput.value = '';
        genreCheckboxes.forEach(cb => cb.checked = false);
        platformCheckboxes.forEach(cb => cb.checked = false);
        priceCheckboxes.forEach(cb => cb.checked = false);
        applyFilters();
    }

    /**
     * Capitalize first letter of string
     */
    function capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    // Event Listeners
    searchInput.addEventListener('input', debounce(applyFilters, 300));

    genreCheckboxes.forEach(cb => {
        cb.addEventListener('change', applyFilters);
    });

    platformCheckboxes.forEach(cb => {
        cb.addEventListener('change', applyFilters);
    });

    priceCheckboxes.forEach(cb => {
        cb.addEventListener('change', applyFilters);
    });

    clearFiltersBtn.addEventListener('click', clearAllFilters);

    // Initial setup - show all games
    applyFilters();
});