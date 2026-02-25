(function () {
    /**
     * Professional IANA TimeZone Detection Engine.
     * Establishes a permanent, daylight-savings-aware handshake with the backend.
     */
    document.addEventListener("DOMContentLoaded", () => {
        const COOKIE_NAME = 'django_timezone';

        // 1. Detect IANA Timezone (e.g., 'Asia/Kolkata')
        // Handles Summer/Winter shifts automatically via the Intl API.
        const detectedTz = Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';

        // 2. Read Existing Cookie
        const getCookie = (name) => {
            const value = `; ${document.cookie}`;
            const parts = value.split(`; ${name}=`);
            if (parts.length === 2) return parts.pop().split(';').shift();
        };

        const storedTz = getCookie(COOKIE_NAME);

        // 3. Logic Gate: Only update if missing or mismatched to reduce DOM writes
        if (storedTz !== detectedTz) {
            console.log(`[Timezone Sync] Updating from ${storedTz} to ${detectedTz}`);

            // 4. Set "Handshake" Cookie
            // path=/: Available globally
            // max-age=31536000: Persist for 1 year
            // SameSite=Lax: Security standard
            document.cookie = `${COOKIE_NAME}=${detectedTz}; path=/; max-age=31536000; SameSite=Lax`;
        } else {
            console.log("[Timezone Sync] Cookie already synchronized.");
        }
    });
})();
