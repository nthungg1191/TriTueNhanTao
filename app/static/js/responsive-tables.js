/* ============================================================
   responsive-tables.js
   Converts <table class="table responsive-cards"> into a list
   of cards on small screens (≤768px).
   ============================================================ */
(function () {
    'use strict';

    const MOBILE_BREAKPOINT = 768;
    let lastIsMobile = null;

    function isMobile() {
        return window.innerWidth <= MOBILE_BREAKPOINT;
    }

    function buildCardView(table) {
        // Avoid duplicating wrapper
        if (table.nextElementSibling && table.nextElementSibling.classList.contains('table-cards-wrapper')) {
            return;
        }

        const thead = table.querySelector('thead');
        if (!thead) return;

        const headers = Array.from(thead.querySelectorAll('th')).map(th => th.textContent.trim());
        const tbody = table.querySelector('tbody');
        if (!tbody) return;

        const wrapper = document.createElement('div');
        wrapper.className = 'table-cards-wrapper';

        const rows = tbody.querySelectorAll('tr');
        rows.forEach((tr) {
            // Skip empty-state rows (typically have a single colspan cell)
            const cells = Array.from(tr.querySelectorAll('td'));
            if (cells.length === 1 && cells[0].hasAttribute('colspan')) {
                const card = document.createElement('div');
                card.className = 'data-card data-card-empty';
                card.style.textAlign = 'center';
                card.style.color = '#94a3b8';
                card.style.padding = '20px';
                card.textContent = cells[0].textContent.trim();
                wrapper.appendChild(card);
                return;
            }

            const card = document.createElement('div');
            card.className = 'data-card';

            cells.forEach((td, idx) => {
                const label = headers[idx] || '';
                const row = document.createElement('div');
                row.className = 'data-card-row';

                const labelEl = document.createElement('div');
                labelEl.className = 'data-card-label';
                labelEl.textContent = label;

                const valueEl = document.createElement('div');
                valueEl.className = 'data-card-value';
                // Use innerHTML to preserve badges / icons / links
                valueEl.innerHTML = td.innerHTML;

                row.appendChild(labelEl);
                row.appendChild(valueEl);
                card.appendChild(row);
            });

            // If the last cell contains forms/buttons, surface them in a dedicated action bar
            const lastCell = cells[cells.length - 1];
            if (lastCell) {
                const actions = lastCell.querySelectorAll('form, .btn, a.btn');
                if (actions.length > 1 || (actions.length === 1 && cells.length > 2)) {
                    const actionBar = document.createElement('div');
                    actionBar.className = 'data-card-actions';
                    // Pull out forms and primary action buttons from the last cell
                    const lastCellHtml = lastCell.innerHTML;
                    // We don't move nodes (avoids breaking event handlers) - duplicate visuals
                    // Just append a small note that actions are in the row above
                    const note = document.createElement('div');
                    note.style.fontSize = '12px';
                    note.style.color = '#94a3b8';
                    note.textContent = '(xem hành động bên dưới)';
                    actionBar.appendChild(note);
                    card.appendChild(actionBar);
                }
            }

            wrapper.appendChild(card);
        });

        table.parentNode.insertBefore(wrapper, table.nextSibling);
    }

    function removeCardView(table) {
        const next = table.nextElementSibling;
        if (next && next.classList.contains('table-cards-wrapper')) {
            next.remove();
        }
    }

    function refresh() {
        const mobile = isMobile();
        if (mobile === lastIsMobile) return;
        lastIsMobile = mobile;

        const tables = document.querySelectorAll('table.responsive-cards');
        tables.forEach(table => {
            if (mobile) {
                buildCardView(table);
            } else {
                removeCardView(table);
            }
        });
    }

    // Run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', refresh);
    } else {
        refresh();
    }

    // Re-run on resize (debounced)
    let resizeTimer;
    window.addEventListener('resize', function () {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(refresh, 150);
    });
})();
