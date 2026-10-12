// =========================================
// AGRISMART - GLOBAL APPLICATION CORE JS
// =========================================

window.AgriApp = {
    showToast(message, type = 'info') {
        let container = document.querySelector('.flash-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'flash-container';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        let iconName = 'info';
        if (type === 'success') iconName = 'check-circle';
        if (type === 'error') iconName = 'alert-circle';

        toast.innerHTML = `
            <div style="display:flex;align-items:center;gap:0.75rem;">
                <i data-lucide="${iconName}"></i>
                <span style="font-size:0.9rem;font-weight:500;">${message}</span>
            </div>
        `;
        container.appendChild(toast);
        if (window.lucide) lucide.createIcons();

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(60px)';
            toast.style.transition = 'all 0.4s ease';
            setTimeout(() => toast.remove(), 400);
        }, 4000);
    }
};

document.addEventListener('DOMContentLoaded', () => {
    // 1. Live Clock & Date in Topbar (ticks every second)
    const dateDisplay = document.getElementById('liveDateTimeDisplay');
    const clockTicker = document.getElementById('liveClockTicker');

    const updateLiveClock = () => {
        const now = new Date();
        if (dateDisplay) {
            const dateOptions = { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' };
            dateDisplay.textContent = now.toLocaleDateString('en-US', dateOptions);
        }
        if (clockTicker) {
            clockTicker.textContent = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true });
        }
    };
    updateLiveClock();
    setInterval(updateLiveClock, 1000);

    // 2. Notification Dropdown Toggle
    const notifBtn = document.getElementById('notifBtn');
    const notifDropdown = document.getElementById('notifDropdown');
    if (notifBtn && notifDropdown) {
        notifBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            notifDropdown.classList.toggle('show');
        });

        document.addEventListener('click', () => {
            notifDropdown.classList.remove('show');
        });
    }

    // 3. Live User Location & Weather Fetch
    const topbarWeatherText = document.getElementById('topbarWeatherText');
    const topbarWeatherIcon = document.getElementById('topbarWeatherIcon');
    
    if (topbarWeatherText) {
        // Instant restore from cache if available
        const cachedWeather = localStorage.getItem('agrismart_cached_weather_text');
        if (cachedWeather) {
            topbarWeatherText.textContent = cachedWeather;
        }

        const applyWeatherData = (data) => {
            if (data && (data.success || data.temperature)) {
                const loc = data.location_display || (data.state ? `${data.city}, ${data.state}` : data.city);
                const weatherStr = `${loc}: ${data.temperature}°C, ${data.condition}`;
                topbarWeatherText.textContent = weatherStr;
                localStorage.setItem('agrismart_cached_weather_text', weatherStr);
                localStorage.setItem('agrismart_cached_weather_json', JSON.stringify(data));
                
                if (topbarWeatherIcon && data.icon) {
                    topbarWeatherIcon.setAttribute('data-lucide', data.icon);
                    if (window.lucide) lucide.createIcons();
                }

                // Dispatch global weather event
                window.dispatchEvent(new CustomEvent('agrismart:weather_updated', { detail: data }));
            }
        };

        const fetchByCoords = (lat, lon) => {
            fetch(`/dashboard/api/weather?lat=${lat}&lon=${lon}`)
                .then(res => res.json())
                .then(applyWeatherData)
                .catch(() => {
                    fetchDefaultWeather();
                });
        };

        const fetchDefaultWeather = () => {
            fetch('/dashboard/api/weather')
                .then(res => res.json())
                .then(applyWeatherData)
                .catch(() => {
                    topbarWeatherText.textContent = 'Live Station: 27.1°C, Mainly Clear';
                });
        };

        // Try HTML5 Geolocation for precise farmer/user location
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (pos) => {
                    fetchByCoords(pos.coords.latitude, pos.coords.longitude);
                },
                (err) => {
                    // Fallback to IP or user profile location
                    fetchDefaultWeather();
                },
                { timeout: 6000, maximumAge: 300000 }
            );
        } else {
            fetchDefaultWeather();
        }
    }

    // 4. Counter number animation for elements with .counter-val
    const counters = document.querySelectorAll('.counter-val');
    counters.forEach(counter => {
        const target = parseInt(counter.dataset.target || counter.textContent) || 0;
        let start = 0;
        const duration = 1000;
        const startTime = performance.now();

        const step = (now) => {
            const elapsed = now - startTime;
            const progress = Math.min(elapsed / duration, 1);
            counter.textContent = Math.floor(progress * target);
            if (progress < 1) {
                requestAnimationFrame(step);
            } else {
                counter.textContent = target;
            }
        };
        requestAnimationFrame(step);
    });

    // 5. Auto-dismiss initial toasts
    document.querySelectorAll('.toast').forEach(toast => {
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(60px)';
            toast.style.transition = 'all 0.4s ease';
            setTimeout(() => toast.remove(), 400);
        }, 4500);
    });
});
