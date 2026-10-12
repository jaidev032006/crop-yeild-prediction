/* =========================================
   AGRISMART - PREDICT & FERTILIZER ENGINE JS
   ========================================= */

document.addEventListener('DOMContentLoaded', () => {
    // Sliders & Value Badges
    const sliders = {
        n: { input: document.getElementById('sliderN'), badge: document.getElementById('valN') },
        p: { input: document.getElementById('sliderP'), badge: document.getElementById('valP') },
        k: { input: document.getElementById('sliderK'), badge: document.getElementById('valK') },
        temp: { input: document.getElementById('sliderTemp'), badge: document.getElementById('valTemp') },
        humid: { input: document.getElementById('sliderHumid'), badge: document.getElementById('valHumid') },
        ph: { input: document.getElementById('sliderPh'), badge: document.getElementById('valPh') },
        rain: { input: document.getElementById('sliderRain'), badge: document.getElementById('valRain') }
    };

    // Initialize slider listeners
    Object.keys(sliders).forEach(key => {
        const item = sliders[key];
        if (item.input && item.badge) {
            item.input.addEventListener('input', () => {
                item.badge.textContent = item.input.value;
                updateSliderFill(item.input);
            });
            updateSliderFill(item.input);
        }
    });

    function updateSliderFill(slider) {
        const min = parseFloat(slider.min) || 0;
        const max = parseFloat(slider.max) || 100;
        const val = parseFloat(slider.value) || 0;
        const percentage = ((val - min) / (max - min)) * 100;
        slider.style.background = `linear-gradient(to right, #10b981 0%, #10b981 ${percentage}%, var(--bg-muted) ${percentage}%, var(--bg-muted) 100%)`;
    }

    // Smoothly animate sliders to target values
    function animateSlidersTo(targetValues, duration = 600) {
        const startValues = {};
        const startTime = performance.now();

        Object.keys(targetValues).forEach(k => {
            if (sliders[k] && sliders[k].input) {
                startValues[k] = parseFloat(sliders[k].input.value);
            }
        });

        function step(now) {
            const elapsed = now - startTime;
            const progress = Math.min(elapsed / duration, 1);
            // Ease out cubic
            const ease = 1 - Math.pow(1 - progress, 3);

            Object.keys(targetValues).forEach(k => {
                if (sliders[k] && sliders[k].input) {
                    const start = startValues[k];
                    const target = targetValues[k];
                    const current = start + (target - start) * ease;
                    const decimals = (k === 'ph' || k === 'temp' || k === 'humid' || k === 'rain') ? 1 : 0;
                    const formatted = current.toFixed(decimals);
                    sliders[k].input.value = formatted;
                    sliders[k].badge.textContent = formatted;
                    updateSliderFill(sliders[k].input);
                }
            });

            if (progress < 1) {
                requestAnimationFrame(step);
            }
        }

        requestAnimationFrame(step);
    }

    // Preset Chips Handlers
    const presetChips = document.querySelectorAll('.preset-chip');
    presetChips.forEach(chip => {
        chip.addEventListener('click', () => {
            presetChips.forEach(c => c.classList.remove('active'));
            chip.classList.add('active');

            const presetData = {
                n: parseFloat(chip.dataset.n),
                p: parseFloat(chip.dataset.p),
                k: parseFloat(chip.dataset.k),
                temp: parseFloat(chip.dataset.temp),
                humid: parseFloat(chip.dataset.humid),
                ph: parseFloat(chip.dataset.ph),
                rain: parseFloat(chip.dataset.rain)
            };

            animateSlidersTo(presetData);
        });
    });

    // Weather Autofill Integration
    const fetchWeatherBtn = document.getElementById('fetchWeatherBtn');
    const weatherCityInput = document.getElementById('weatherCityInput');
    
    if (fetchWeatherBtn) {
        fetchWeatherBtn.addEventListener('click', async () => {
            const city = weatherCityInput ? weatherCityInput.value.trim() : 'Mumbai';
            if (!city) {
                window.AgriApp?.showToast('Please enter a city name.', 'error');
                return;
            }

            fetchWeatherBtn.disabled = true;
            fetchWeatherBtn.innerHTML = `<i data-lucide="loader-2" class="spin"></i> Fetching...`;
            if (window.lucide) lucide.createIcons();

            try {
                const res = await fetch(`/dashboard/api/weather?city=${encodeURIComponent(city)}`);
                const data = await res.json();

                if (data.success) {
                    animateSlidersTo({
                        temp: data.temperature,
                        humid: data.humidity,
                        rain: data.rainfall
                    });
                    window.AgriApp?.showToast(`Loaded live weather for ${data.city}: ${data.temperature}°C, ${data.humidity}% Humidity`, 'success');
                } else {
                    window.AgriApp?.showToast(data.message || 'Could not fetch weather data.', 'error');
                }
            } catch (err) {
                window.AgriApp?.showToast('Network error while retrieving weather parameters.', 'error');
            } finally {
                fetchWeatherBtn.disabled = false;
                fetchWeatherBtn.innerHTML = `<i data-lucide="cloud-sun"></i> Autofill Weather`;
                if (window.lucide) lucide.createIcons();
            }
        });
    }

    // Form Submission & Prediction Pipeline
    const predictForm = document.getElementById('cropPredictForm');
    const seedlingLoader = document.getElementById('seedlingLoader');
    const resultContainer = document.getElementById('resultContainer');
    const initialPlaceholder = document.getElementById('initialPlaceholder');
    const submitBtn = document.getElementById('submitPredictBtn');

    if (predictForm) {
        predictForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Prepare Payload
            const payload = {
                n: parseFloat(sliders.n.input.value),
                p: parseFloat(sliders.p.input.value),
                k: parseFloat(sliders.k.input.value),
                temp: parseFloat(sliders.temp.input.value),
                humid: parseFloat(sliders.humid.input.value),
                ph: parseFloat(sliders.ph.input.value),
                rain: parseFloat(sliders.rain.input.value)
            };

            // Transition UI to Loader
            if (initialPlaceholder) initialPlaceholder.style.display = 'none';
            if (resultContainer) resultContainer.style.display = 'none';
            if (seedlingLoader) seedlingLoader.style.display = 'flex';
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = `<i data-lucide="loader" class="spin"></i> Analyzing Agro-Climatic Data...`;
                if (window.lucide) lucide.createIcons();
            }

            try {
                const res = await fetch('/predict/api/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                const data = await res.json();

                if (data.success) {
                    // Small delay for smooth visual appreciation of the seedling sprout loader
                    setTimeout(() => {
                        renderPredictionResult(data);
                    }, 800);
                } else {
                    window.AgriApp?.showToast(data.message || 'Prediction failed.', 'error');
                    if (seedlingLoader) seedlingLoader.style.display = 'none';
                    if (initialPlaceholder) initialPlaceholder.style.display = 'flex';
                }
            } catch (err) {
                window.AgriApp?.showToast('Server connection error. Please try again.', 'error');
                if (seedlingLoader) seedlingLoader.style.display = 'none';
                if (initialPlaceholder) initialPlaceholder.style.display = 'flex';
            } finally {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = `<i data-lucide="sparkles"></i> Generate AI Crop Recommendation`;
                    if (window.lucide) lucide.createIcons();
                }
            }
        });
    }

    // =========================================
    // UNIFIED LOCATION SELECTION & INTELLIGENCE
    // =========================================
    const btnModeLocation = document.getElementById('btnModeLocation');
    const btnModeManual = document.getElementById('btnModeManual');
    const btnSwitchToManual = document.getElementById('btnSwitchToManual');
    const locationPickerSection = document.getElementById('locationPickerSection');
    const manualSlidersSection = document.getElementById('manualSlidersSection');
    const presetsStrip = document.getElementById('presetsStrip');

    const selectState = document.getElementById('selectState');
    const selectDistrict = document.getElementById('selectDistrict');
    const districtTelemetryBox = document.getElementById('districtTelemetryBox');
    const submitLocationBtn = document.getElementById('submitLocationBtn');
    const btnTryQuickAnalysis = document.getElementById('btnTryQuickAnalysis');

    let currentLocationProfile = null;

    function setMode(mode) {
        if (mode === 'location') {
            btnModeLocation?.classList.add('active');
            btnModeManual?.classList.remove('active');
            if (locationPickerSection) locationPickerSection.style.display = 'block';
            if (manualSlidersSection) manualSlidersSection.style.display = 'none';
            if (presetsStrip) presetsStrip.style.display = 'none';
        } else {
            btnModeManual?.classList.add('active');
            btnModeLocation?.classList.remove('active');
            if (locationPickerSection) locationPickerSection.style.display = 'none';
            if (manualSlidersSection) manualSlidersSection.style.display = 'block';
            if (presetsStrip) presetsStrip.style.display = 'flex';
        }
    }

    if (btnModeLocation) btnModeLocation.addEventListener('click', () => setMode('location'));
    if (btnModeManual) btnModeManual.addEventListener('click', () => setMode('manual'));
    if (btnSwitchToManual) btnSwitchToManual.addEventListener('click', () => setMode('manual'));

    // Populate Districts when State changes
    async function loadDistricts(stateName, autoSelectFirst = true) {
        if (!stateName || !selectDistrict) return;
        selectDistrict.innerHTML = '<option value="" disabled selected>Loading districts...</option>';
        try {
            const res = await fetch(`/predict/api/locations?state=${encodeURIComponent(stateName)}`);
            const data = await res.json();
            if (data.success && data.locations && data.locations.length > 0) {
                selectDistrict.innerHTML = '<option value="" disabled>-- Select District --</option>';
                data.locations.forEach((loc, idx) => {
                    const opt = document.createElement('option');
                    opt.value = loc.id;
                    opt.textContent = `${loc.address} (${loc.crops.slice(0, 3).join(', ')})`;
                    if (autoSelectFirst && idx === 0) {
                        opt.selected = true;
                    }
                    selectDistrict.appendChild(opt);
                });

                if (autoSelectFirst && data.locations.length > 0) {
                    loadLocationProfile(data.locations[0].id);
                }
            } else {
                selectDistrict.innerHTML = '<option value="" disabled selected>No districts found</option>';
            }
        } catch (err) {
            console.error('Failed to load districts:', err);
            selectDistrict.innerHTML = '<option value="" disabled selected>Error loading districts</option>';
        }
    }

    // Load full soil & telemetry profile for a selected district
    async function loadLocationProfile(locationId) {
        if (!locationId) return;
        try {
            const res = await fetch(`/predict/api/location-profile?id=${locationId}`);
            const json = await res.json();
            if (json.success && json.data) {
                currentLocationProfile = json.data;
                renderLocationTelemetry(json.data);
            }
        } catch (err) {
            console.error('Failed to load location profile:', err);
        }
    }

    function renderLocationTelemetry(data) {
        if (!districtTelemetryBox) return;
        districtTelemetryBox.style.display = 'block';

        const loc = data.location;
        const weather = data.weather;
        const sd = loc.soil_distributions;
        const est = loc.estimated_inputs;

        // Title and GPS
        const nameEl = document.getElementById('telemetryLocationName');
        const addrEl = document.getElementById('telemetryFormattedAddr');
        const gpsEl = document.getElementById('telemetryGpsCoords');
        if (nameEl) nameEl.textContent = `${loc.address}, ${loc.region}`;
        if (addrEl) addrEl.textContent = loc.formatted_address || loc.address;
        if (gpsEl) gpsEl.textContent = `${loc.latitude.toFixed(2)}° N, ${loc.longitude.toFixed(2)}° E`;

        // Soil badges with level classes
        function setBadge(id, estId, dominant, estVal, unit, isPh = false) {
            const badge = document.getElementById(id);
            const estSpan = document.getElementById(estId);
            if (!badge || !estSpan) return;
            badge.textContent = dominant;
            badge.className = 'soil-badge-val';
            
            const domLower = (dominant || '').toLowerCase();
            if (domLower.includes('high')) badge.classList.add('val-high');
            else if (domLower.includes('med')) badge.classList.add('val-med');
            else if (domLower.includes('low')) badge.classList.add('val-low');
            else if (domLower.includes('neut')) badge.classList.add('val-neutral');
            else if (domLower.includes('acid')) badge.classList.add('val-acidic');
            else if (domLower.includes('alk')) badge.classList.add('val-alkaline');

            estSpan.textContent = isPh ? `pH ~ ${estVal}` : `~ ${estVal} ${unit}`;
        }

        setBadge('telemetryNBadge', 'telemetryNEst', sd.nitrogen.dominant, est.n, 'mg/kg');
        setBadge('telemetryPBadge', 'telemetryPEst', sd.phosphorus.dominant, est.p, 'mg/kg');
        setBadge('telemetryKBadge', 'telemetryKEst', sd.potassium.dominant, est.k, 'mg/kg');
        setBadge('telemetryPhBadge', 'telemetryPhEst', sd.ph.dominant, est.ph, '', true);

        // Traditional crops tags
        const cropsListEl = document.getElementById('telemetryCropsList');
        if (cropsListEl) {
            cropsListEl.innerHTML = '';
            if (loc.traditional_crops && loc.traditional_crops.length > 0) {
                loc.traditional_crops.forEach(crop => {
                    const tag = document.createElement('span');
                    tag.className = 'crop-tag';
                    tag.textContent = crop;
                    cropsListEl.appendChild(tag);
                });
            } else {
                cropsListEl.innerHTML = '<span style="font-size:0.8rem;color:var(--text-muted);">Multiple field crops documented</span>';
            }
        }

        // Live weather text banner
        const weatherEl = document.getElementById('telemetryWeatherText');
        if (weatherEl) {
            weatherEl.textContent = `Live Weather: ${weather.temperature}°C, ${weather.humidity}% Humidity, ${weather.rainfall}mm Rainfall (${weather.source})`;
        }

        // Auto-prime manual sliders with this district's calibrated data
        animateSlidersTo({
            n: est.n,
            p: est.p,
            k: est.k,
            temp: weather.temperature,
            humid: weather.humidity,
            ph: est.ph,
            rain: weather.rainfall
        });

        if (window.lucide) lucide.createIcons();
    }

    if (selectState) {
        selectState.addEventListener('change', () => {
            loadDistricts(selectState.value, true);
        });
        // Initial load for default state
        if (selectState.value) {
            loadDistricts(selectState.value, true);
        }
    }

    if (selectDistrict) {
        selectDistrict.addEventListener('change', () => {
            loadLocationProfile(selectDistrict.value);
        });
    }

    // Execute Location-Based Recommendation Pipeline
    async function executeLocationPredict() {
        if (!currentLocationProfile && selectDistrict && selectDistrict.value) {
            await loadLocationProfile(selectDistrict.value);
        }

        const locId = selectDistrict ? selectDistrict.value : null;
        if (!locId) {
            window.AgriApp?.showToast('Please select a district first.', 'error');
            return;
        }

        // Transition UI to Loader
        if (initialPlaceholder) initialPlaceholder.style.display = 'none';
        if (resultContainer) resultContainer.style.display = 'none';
        if (seedlingLoader) seedlingLoader.style.display = 'flex';
        if (submitLocationBtn) {
            submitLocationBtn.disabled = true;
            submitLocationBtn.innerHTML = `<i data-lucide="loader" class="spin"></i> Analyzing District Agro-Climatic Data...`;
            if (window.lucide) lucide.createIcons();
        }

        try {
            const res = await fetch('/predict/api/location-predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    location_id: locId,
                    location_name: selectDistrict.options[selectDistrict.selectedIndex]?.text || ''
                })
            });

            const data = await res.json();
            if (data.success) {
                setTimeout(() => {
                    renderPredictionResult(data);
                }, 800);
            } else {
                window.AgriApp?.showToast(data.message || 'Location analysis failed.', 'error');
                if (seedlingLoader) seedlingLoader.style.display = 'none';
                if (initialPlaceholder) initialPlaceholder.style.display = 'flex';
            }
        } catch (err) {
            window.AgriApp?.showToast('Network error while processing location recommendation.', 'error');
            if (seedlingLoader) seedlingLoader.style.display = 'none';
            if (initialPlaceholder) initialPlaceholder.style.display = 'flex';
        } finally {
            if (submitLocationBtn) {
                submitLocationBtn.disabled = false;
                submitLocationBtn.innerHTML = `<i data-lucide="sparkles"></i> Analyze Location & Recommend Perfect Crop`;
                if (window.lucide) lucide.createIcons();
            }
        }
    }

    if (submitLocationBtn) submitLocationBtn.addEventListener('click', executeLocationPredict);
    if (btnTryQuickAnalysis) btnTryQuickAnalysis.addEventListener('click', executeLocationPredict);

    function renderPredictionResult(data) {
        if (seedlingLoader) seedlingLoader.style.display = 'none';
        if (resultContainer) resultContainer.style.display = 'flex';

        // 1. Populate Text Badges & Metadata
        document.getElementById('resultCropName').textContent = data.crop;
        document.getElementById('resultConfidence').textContent = `${data.confidence}%`;
        document.getElementById('resultYield').textContent = `${data.yield_estimate} t/ha`;
        document.getElementById('resultSeason').textContent = data.metadata.season || 'Year-round';
        document.getElementById('resultSoil').textContent = data.metadata.soil_type || 'Loamy Soil';
        document.getElementById('resultCropDesc').textContent = data.metadata.desc || '';

        // Regional Location Match Badge
        const regionalBanner = document.getElementById('resultRegionalBanner');
        const regionalLocEl = document.getElementById('resultRegionalLocation');
        const regionalNoteEl = document.getElementById('resultRegionalNote');

        if (regionalBanner) {
            if (data.location) {
                regionalBanner.style.display = 'flex';
                if (regionalLocEl) regionalLocEl.textContent = `${data.location.address}, ${data.location.region}`;
                const cropsListStr = (data.location.traditional_crops || []).slice(0, 3).join(', ');
                if (regionalNoteEl) {
                    regionalNoteEl.textContent = `Field verified for this zone (${cropsListStr ? 'historically grown with ' + cropsListStr : 'optimal soil and climatic conditions'}).`;
                }
            } else {
                regionalBanner.style.display = 'none';
            }
        }

        // Download Report Link
        const reportBtn = document.getElementById('downloadReportBtn');
        if (reportBtn && data.prediction_id) {
            reportBtn.href = `/predict/report/${data.prediction_id}`;
        }

        // 2. Animate Circular Progress Ring for Yield Efficiency
        const ring = document.getElementById('yieldRingProgress');
        const ringVal = document.getElementById('yieldRingValue');
        if (ring) {
            const circumference = 314; // 2 * pi * 50
            const offset = circumference - (data.yield_efficiency / 100) * circumference;
            ring.style.strokeDashoffset = offset;
        }
        if (ringVal) {
            animateNumberCounter(ringVal, data.yield_efficiency, '%');
        }

        // 3. Trigger SIGNATURE FERTILIZER ANIMATION
        triggerFertilizerAnimation(data.fertilizer_recommendation);

        if (window.lucide) lucide.createIcons();
    }

    function triggerFertilizerAnimation(adviceText) {
        const stage = document.getElementById('fertPlantStage');
        const emitter = document.getElementById('granuleEmitter');
        const adviceContainer = document.getElementById('fertAdviceList');

        if (!stage || !emitter || !adviceContainer) return;

        // Reset Stage
        stage.className = 'morph-plant-svg stage-1';
        emitter.innerHTML = '';
        adviceContainer.innerHTML = '';

        // Spawn falling fertilizer particles
        const particleColors = ['n-dot', 'p-dot', 'k-dot'];
        for (let i = 0; i < 28; i++) {
            const dot = document.createElement('div');
            const colorClass = particleColors[i % 3];
            dot.className = `granule-dot ${colorClass}`;
            dot.style.left = `${Math.random() * 85 + 5}%`;
            dot.style.animationDelay = `${Math.random() * 1.5}s`;
            dot.style.animationDuration = `${1.2 + Math.random() * 0.6}s`;
            emitter.appendChild(dot);
        }

        // Stage 1 -> Stage 2 -> Stage 3 Plant Morph
        setTimeout(() => {
            stage.className = 'morph-plant-svg stage-2';
        }, 800);

        setTimeout(() => {
            stage.className = 'morph-plant-svg stage-3';
        }, 1800);

        // Staggered Typewriter / Line-by-line reveal of advice text
        const lines = (adviceText || '').split('\n').filter(l => l.trim().length > 0);
        
        lines.forEach((line, index) => {
            const item = document.createElement('div');
            item.className = 'fert-advice-item';
            
            // Format bold text
            let formattedLine = line.replace(/•/g, '').trim();
            formattedLine = formattedLine.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            item.innerHTML = `<i data-lucide="check-circle-2" style="width:16px;height:16px;color:#10b981;display:inline-block;vertical-align:middle;margin-right:6px;"></i> ${formattedLine}`;
            
            adviceContainer.appendChild(item);

            setTimeout(() => {
                item.classList.add('revealed');
                if (window.lucide) lucide.createIcons();
            }, 600 + index * 400);
        });
    }

    function animateNumberCounter(element, target, suffix = '') {
        const start = 0;
        const duration = 1200;
        const startTime = performance.now();

        function step(now) {
            const elapsed = now - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const current = Math.floor(progress * target);
            element.textContent = `${current}${suffix}`;
            if (progress < 1) {
                requestAnimationFrame(step);
            } else {
                element.textContent = `${target}${suffix}`;
            }
        }
        requestAnimationFrame(step);
    }
});
