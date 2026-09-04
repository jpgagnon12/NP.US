const toggle = document.querySelector(".nav-toggle");
const nav = document.querySelector(".site-nav");
const recentNav = document.querySelector("#recent-parks");
const pageSlug = document.body.dataset.pageSlug;
const pageTitle = document.body.dataset.pageTitle;
const pageDepth = Number(document.body.dataset.pageDepth || "0");
const headerSearch = document.querySelector(".header-search");
const headerSearchInput = document.querySelector("#header-park-search");
const headerSearchResults = document.querySelector("#header-search-results");
const headerSearchData = document.querySelector("#header-search-data");

if (toggle && nav) {
  toggle.addEventListener("click", () => {
    const open = nav.classList.toggle("open");
    toggle.setAttribute("aria-expanded", String(open));
  });
}

const storageKey = "nationalParkCam.recentParks";
const nationalParkCamBaseUrl = "https://www.nationalparkcam.com";
const noCameraParkSlugs = new Set([
  "badlands-national-park",
  "biscayne-national-park",
  "canyonlands-national-park",
  "capitol-reef-national-park",
  "carlsbad-caverns-national-park",
  "congaree-national-park",
  "cuyahoga-valley-national-park",
  "death-valley-national-park",
  "dry-tortugas-national-park",
  "gates-of-the-arctic-national-park",
  "gateway-arch-national-park",
  "great-basin-national-park",
  "great-sand-dunes-national-park",
  "hot-springs-national-park",
  "indiana-dunes-national-park",
  "kenai-fjords-national-park",
  "kobuk-valley-national-park",
  "lake-clark-national-park",
  "mesa-verde-national-park",
  "national-park-of-american-samoa",
  "pinnacles-national-park",
  "saguaro-national-park",
  "voyageurs-national-park",
  "white-sands-national-park",
  "wind-cave-national-park",
]);

const getParkHref = (slug) =>
  noCameraParkSlugs.has(slug)
    ? `${pageDepth > 0 ? "" : "parks/"}${slug}.html`
    : `${nationalParkCamBaseUrl}/parks/${slug}`;

const readRecentParks = () => {
  try {
    return JSON.parse(localStorage.getItem(storageKey) || "[]");
  } catch {
    return [];
  }
};

const writeRecentParks = (items) => {
  localStorage.setItem(storageKey, JSON.stringify(items.slice(0, 5)));
};

const renderRecentParks = () => {
  if (!recentNav) return;
  const items = readRecentParks();
  recentNav.replaceChildren();
  if (!items.length) {
    recentNav.hidden = true;
    return;
  }
  recentNav.hidden = false;
  const label = document.createElement("span");
  label.textContent = "Recent";
  recentNav.append(label);
  for (const item of items.slice(0, 5)) {
    const link = document.createElement("a");
    link.href = getParkHref(item.slug);
    if (!noCameraParkSlugs.has(item.slug)) {
      link.target = "_blank";
      link.rel = "noopener";
    }
    link.textContent = item.shortTitle || item.title;
    if (item.slug === pageSlug) link.setAttribute("aria-current", "page");
    recentNav.append(link);
  }
};

if (pageSlug && pageSlug !== "national-park-webcam-home" && pageSlug !== "resources") {
  const shortTitle = pageTitle
    .replace("National and State Parks Webcams", "")
    .replace("National Parks Webcams", "")
    .replace("National Park Webcams", "")
    .replace("National Park", "")
    .replace("Webcams", "")
    .replace("Guide", "")
    .trim();
  const nextRecent = [
    { slug: pageSlug, title: pageTitle, shortTitle: shortTitle || pageTitle },
    ...readRecentParks().filter((item) => item.slug !== pageSlug),
  ];
  writeRecentParks(nextRecent);
}

renderRecentParks();

const getHeaderSearchEntries = () => {
  if (!headerSearchData) return [];
  try {
    return JSON.parse(headerSearchData.textContent || "[]");
  } catch {
    return [];
  }
};

const headerSearchEntries = getHeaderSearchEntries();
const closeHeaderSearch = () => {
  if (!headerSearchResults || !headerSearchInput) return;
  headerSearchResults.hidden = true;
  headerSearchInput.setAttribute("aria-expanded", "false");
};

const openHeaderSearch = () => {
  if (!headerSearchResults || !headerSearchInput) return;
  headerSearchResults.hidden = false;
  headerSearchInput.setAttribute("aria-expanded", "true");
};

const goToHeaderSearchEntry = (entry) => {
  if (!entry) return;
  if (entry.external) {
    window.open(entry.href, "_blank", "noopener");
    return;
  }
  window.location.href = entry.href;
};

const renderHeaderSearchResults = () => {
  if (!headerSearchInput || !headerSearchResults) return;
  const query = headerSearchInput.value.trim().toLowerCase();
  headerSearchResults.replaceChildren();
  if (!query) {
    closeHeaderSearch();
    return;
  }
  const matches = headerSearchEntries
    .filter((entry) => `${entry.label} ${entry.title}`.toLowerCase().includes(query))
    .slice(0, 6);
  if (!matches.length) {
    const empty = document.createElement("div");
    empty.className = "header-search-empty";
    empty.textContent = "No parks found";
    headerSearchResults.append(empty);
    openHeaderSearch();
    return;
  }
  for (const entry of matches) {
    const option = document.createElement("button");
    option.type = "button";
    option.className = "header-search-option";
    option.setAttribute("role", "option");
    option.innerHTML = `<strong>${entry.label}</strong><span>${entry.type}</span>`;
    option.addEventListener("click", () => goToHeaderSearchEntry(entry));
    headerSearchResults.append(option);
  }
  openHeaderSearch();
};

if (headerSearch && headerSearchInput && headerSearchResults) {
  headerSearchInput.addEventListener("input", renderHeaderSearchResults);
  headerSearchInput.addEventListener("focus", renderHeaderSearchResults);
  headerSearch.addEventListener("submit", (event) => {
    event.preventDefault();
    const first = headerSearchResults.querySelector(".header-search-option");
    if (first) {
      first.click();
      return;
    }
    const query = headerSearchInput.value.trim().toLowerCase();
    const exact = headerSearchEntries.find((entry) => `${entry.label} ${entry.title}`.toLowerCase().includes(query));
    goToHeaderSearchEntry(exact);
  });
  document.addEventListener("click", (event) => {
    if (!headerSearch.contains(event.target)) closeHeaderSearch();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeHeaderSearch();
  });
}

const heroVideoData = document.querySelector("#hero-video-data");
const heroVideoIframe = document.querySelector("#hero-video-iframe");
const heroVideoPark = document.querySelector("#hero-video-park");
const heroVideoTitle = document.querySelector("#hero-video-title");
const heroVideoLink = document.querySelector("#hero-video-link");

const withAutoplay = (url) => {
  try {
    const nextUrl = new URL(url);
    nextUrl.searchParams.set("autoplay", "1");
    nextUrl.searchParams.set("mute", "1");
    nextUrl.searchParams.set("playsinline", "1");
    nextUrl.searchParams.set("rel", "0");
    if (window.location.origin && window.location.origin !== "null") {
      nextUrl.searchParams.set("origin", window.location.origin);
    }
    return nextUrl.toString();
  } catch {
    return url;
  }
};

if (heroVideoData && heroVideoIframe) {
  try {
    const videos = JSON.parse(heroVideoData.textContent || "[]");
    const video = videos[Math.floor(Math.random() * videos.length)];
    if (video) {
      heroVideoIframe.src = withAutoplay(video.url);
      heroVideoIframe.title = video.label;
      if (heroVideoPark) heroVideoPark.textContent = video.park;
      if (heroVideoTitle) heroVideoTitle.textContent = video.label;
      if (heroVideoLink) heroVideoLink.href = video.href;
    }
  } catch {
    heroVideoIframe.src = withAutoplay(heroVideoIframe.src);
  }
}

const search = document.querySelector("#park-search");
const cards = Array.from(document.querySelectorAll(".park-card"));
const mapButtons = [];

const initSimpleParkMaps = () => {
  if (!window.L) return;
  const parkMaps = Array.from(document.querySelectorAll("[data-park-map]"));
  for (const el of parkMaps) {
    const lat = Number(el.dataset.lat);
    const lng = Number(el.dataset.lng);
    if (!Number.isFinite(lat) || !Number.isFinite(lng)) continue;
    const map = L.map(el, {
      scrollWheelZoom: false,
      dragging: true,
      zoomControl: true,
      attributionControl: false,
    });
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 18,
    }).addTo(map);
    L.marker([lat, lng]).addTo(map);
    map.setView([lat, lng], 8);
  }
};

initSimpleParkMaps();

if (search) {
  const filterParkCards = () => {
    const query = search.value.trim().toLowerCase();
    for (const card of cards) {
      const title = card.dataset.title || "";
      card.hidden = query.length > 0 && !title.includes(query);
    }
    for (const button of mapButtons) {
      const title = button.dataset.title || "";
      button.hidden = query.length > 0 && !title.includes(query);
    }
  };
  search.addEventListener("input", filterParkCards);

  const searchParams = new URLSearchParams(window.location.search);
  const initialParkQuery = searchParams.get("q");
  if (initialParkQuery) {
    search.value = initialParkQuery;
    filterParkCards();
    document.querySelector("#parks")?.scrollIntoView({ block: "start" });
  }
}

const mapEl = document.querySelector("#webcam-map");
const mapDataEl = document.querySelector("#park-map-data");

if (mapEl && mapDataEl && window.L) {
  const parks = JSON.parse(mapDataEl.textContent || "[]").filter((park) => Number(park.cams) > 0);
  const map = L.map(mapEl, {
    scrollWheelZoom: false,
    worldCopyJump: true,
  });

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    maxZoom: 18,
  }).addTo(map);

  const titleEl = document.querySelector("#map-active-title");
  const metaEl = document.querySelector("#map-active-meta");
  const linkEl = document.querySelector("#map-active-link");
  const listEl = document.querySelector("#map-list");
  const markers = new Map();
  const bounds = [];

  const activatePark = (park, options = {}) => {
    const shouldFocus = options.focus ?? true;
    const shouldOpenPopup = options.popup ?? true;
    if (!park) return;
    if (titleEl) titleEl.textContent = park.fullTitle;
    if (metaEl) {
      metaEl.textContent = "Open this park page on NationalParkCam.com for webcams and planning links.";
    }
    if (linkEl) linkEl.href = park.href;
    for (const button of mapButtons) {
      button.classList.toggle("active", button.dataset.slug === park.slug);
    }
    const marker = markers.get(park.slug);
    if (marker) {
      if (shouldOpenPopup) {
        marker.openPopup();
      }
      if (shouldFocus) {
        map.flyTo([park.lat, park.lng], Math.max(map.getZoom(), 5), { duration: 0.6 });
      }
    }
  };

  for (const park of parks) {
    bounds.push([park.lat, park.lng]);
    const marker = L.marker([park.lat, park.lng], {
      icon: L.divIcon({
        className: "",
        html: `<span class="cam-marker${park.cams ? "" : " no-live"}">${park.cams || ""}</span>`,
        iconSize: [34, 34],
        iconAnchor: [17, 17],
      }),
      title: park.fullTitle,
    }).addTo(map);

    marker.bindPopup(
      `<div class="map-popup"><strong>${park.fullTitle}</strong><p><a href="${park.href}" target="_blank" rel="noopener">Open live cams</a></p></div>`
    );
    marker.on("click", () => activatePark(park));
    markers.set(park.slug, marker);

    if (listEl) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "map-park-button";
      button.dataset.slug = park.slug;
      button.dataset.title = `${park.title} ${park.fullTitle}`.toLowerCase();
      button.innerHTML = `<strong>${park.title}</strong><span>Open on NationalParkCam.com</span>`;
      button.addEventListener("click", () => activatePark(park));
      listEl.append(button);
      mapButtons.push(button);
    }
  }

  if (bounds.length) {
    map.fitBounds(bounds, { padding: [35, 35] });
    activatePark(parks.find((park) => park.slug === "yellowstone-webcam") || parks[0], {
      focus: false,
      popup: false,
    });
  }
}

const weatherSection = document.querySelector(".weather-section[data-lat][data-lng]");
const refreshImages = Array.from(document.querySelectorAll("img[data-refresh-src]"));
const imageFrames = Array.from(document.querySelectorAll(".webcam-image-media[data-full-src], .guide-image-media[data-full-src]"));

if (imageFrames.length) {
  const viewer = document.createElement("div");
  viewer.className = "image-viewer";
  viewer.hidden = true;
  viewer.innerHTML = `
    <button class="image-viewer-close" type="button" aria-label="Close larger image">&times;</button>
    <figure>
      <img alt="">
      <figcaption></figcaption>
    </figure>
  `;
  document.body.append(viewer);

  const viewerImage = viewer.querySelector("img");
  const viewerCaption = viewer.querySelector("figcaption");
  const viewerClose = viewer.querySelector("button");
  const closeViewer = () => {
    viewer.hidden = true;
    document.body.classList.remove("image-viewer-open");
    viewerImage.removeAttribute("src");
    viewerImage.classList.remove("image-viewer-load-error");
  };
  const openViewer = (frame) => {
    if (frame.dataset.nationalparkcamUrl) {
      window.location.href = frame.dataset.nationalparkcamUrl;
      return;
    }
    const image = frame.querySelector("img");
    const title = frame.dataset.title || image?.alt || "Park image";
    const source = image?.currentSrc || image?.src || frame.dataset.fullSrc;
    viewerImage.classList.remove("image-viewer-load-error");
    viewerImage.src = source;
    viewerImage.alt = title;
    viewerCaption.textContent = title;
    viewer.hidden = false;
    document.body.classList.add("image-viewer-open");
    viewerClose.focus();
  };

  viewerImage.addEventListener("error", () => {
    viewerImage.classList.add("image-viewer-load-error");
    viewerCaption.textContent = "This image is temporarily unavailable.";
  });

  for (const frame of imageFrames) {
    const title = frame.dataset.title || frame.querySelector("img")?.alt || "";
    frame.tabIndex = 0;
    frame.setAttribute("role", "button");
    frame.setAttribute("aria-label", `Open larger image${title ? `: ${title}` : ""}`);
    frame.addEventListener("click", () => openViewer(frame));
    frame.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        openViewer(frame);
      }
    });
  }

  viewer.addEventListener("click", (event) => {
    if (event.target === viewer || event.target.closest(".image-viewer-close")) {
      closeViewer();
    }
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !viewer.hidden) closeViewer();
  });
}

if (refreshImages.length) {
  const refreshWebcamImages = () => {
    const cacheBust = Date.now();
    for (const image of refreshImages) {
      const base = image.dataset.refreshSrc;
      if (base.includes("cameras.americanalpineclub.org") || base.includes("phenocam.nau.edu")) {
        image.src = base;
        continue;
      }
      image.src = `${base}${base.includes("?") ? "&" : "?"}t=${cacheBust}`;
    }
  };
  refreshWebcamImages();
  window.setInterval(refreshWebcamImages, 60000);
}

const formatTemp = (value, unit) => {
  if (value === null || value === undefined) return "";
  return `${Math.round(value)}°${unit === "F" ? "F" : unit}`;
};

const fahrenheitToCelsius = (value) => (value - 32) * 5 / 9;

const displayTemp = (valueF, unit) => {
  const numericValue = Number(valueF);
  if (!Number.isFinite(numericValue)) return "";
  return formatTemp(unit === "C" ? fahrenheitToCelsius(numericValue) : numericValue, unit);
};

let currentWeatherUnit = localStorage.getItem("temperatureUnit") === "C" ? "C" : "F";

const renderWeatherError = (message) => {
  document.querySelectorAll("[data-weather-hourly], [data-weather-daily]").forEach((el) => {
    el.textContent = message;
    el.classList.add("weather-unavailable");
  });
};

const weatherCodeText = {
  0: "Clear",
  1: "Mostly clear",
  2: "Partly cloudy",
  3: "Cloudy",
  45: "Fog",
  48: "Freezing fog",
  51: "Light drizzle",
  53: "Drizzle",
  55: "Heavy drizzle",
  61: "Light rain",
  63: "Rain",
  65: "Heavy rain",
  71: "Light snow",
  73: "Snow",
  75: "Heavy snow",
  80: "Light showers",
  81: "Showers",
  82: "Heavy showers",
  95: "Thunderstorms",
};

const conditionsDashboards = Array.from(document.querySelectorAll("[data-conditions-dashboard]"));

const setConditionCard = (card, status, message, className = "") => {
  if (!card) return;
  const statusEl = card.querySelector("strong");
  const messageEl = card.querySelector("p");
  card.classList.remove("condition-good", "condition-watch", "condition-alert");
  if (className) card.classList.add(className);
  if (statusEl) statusEl.textContent = status;
  if (messageEl) messageEl.textContent = message;
};

const aqiLabel = (aqi) => {
  if (aqi <= 50) return ["Good", "condition-good"];
  if (aqi <= 100) return ["Moderate", "condition-watch"];
  if (aqi <= 150) return ["Unhealthy for sensitive groups", "condition-watch"];
  if (aqi <= 200) return ["Unhealthy", "condition-alert"];
  if (aqi <= 300) return ["Very unhealthy", "condition-alert"];
  return ["Hazardous", "condition-alert"];
};

const initConditionsDashboard = (dashboard) => {
  const parkCode = dashboard.dataset.parkCode;
  const parkName = dashboard.dataset.parkName || "this park";
  const lat = dashboard.dataset.lat;
  const lng = dashboard.dataset.lng;
  const roadUrl = dashboard.dataset.roadUrl;
  const officialUrl = dashboard.dataset.officialUrl;
  const alertsCard = dashboard.querySelector("[data-condition-alerts]");
  const airCard = dashboard.querySelector("[data-condition-air]");
  const roadsCard = dashboard.querySelector("[data-condition-roads]");

  if (parkCode && alertsCard) {
    fetch(`https://developer.nps.gov/api/v1/alerts?parkCode=${encodeURIComponent(parkCode)}&api_key=DEMO_KEY`)
      .then((response) => {
        if (!response.ok) throw new Error("Alerts unavailable");
        return response.json();
      })
      .then((payload) => {
        const alerts = Array.isArray(payload.data) ? payload.data : [];
        if (!alerts.length) {
          setConditionCard(alertsCard, "No active alerts", `NPS currently lists no active ${parkName} alerts.`, "condition-good");
          return;
        }
        const firstAlert = alerts[0]?.title ? `Latest: ${alerts[0].title}` : "Open NPS for current alert details.";
        setConditionCard(alertsCard, `${alerts.length} active alert${alerts.length === 1 ? "" : "s"}`, firstAlert, "condition-alert");
      })
      .catch(() => {
        setConditionCard(alertsCard, "Check NPS", "Alerts are temporarily unavailable here. Open the official park conditions page.", "condition-watch");
      });
  } else if (alertsCard) {
    setConditionCard(alertsCard, "Official Updates", "Use the official park site for current notices, advisories, and closures.", "condition-watch");
    const link = alertsCard.querySelector("a");
    if (link && officialUrl) link.href = officialUrl;
  }

  if (lat && lng && airCard) {
    fetch(
      `https://air-quality-api.open-meteo.com/v1/air-quality?latitude=${encodeURIComponent(lat)}&longitude=${encodeURIComponent(lng)}&hourly=us_aqi,pm2_5,ozone&timezone=auto&forecast_days=1`
    )
      .then((response) => {
        if (!response.ok) throw new Error("Air quality unavailable");
        return response.json();
      })
      .then((payload) => {
        const times = payload.hourly?.time || [];
        const aqiValues = payload.hourly?.us_aqi || [];
        const pm25Values = payload.hourly?.pm2_5 || [];
        const now = Date.now();
        const closestIndex = times.reduce((bestIndex, timeValue, index) => {
          const bestDiff = Math.abs(new Date(times[bestIndex] || 0).getTime() - now);
          const nextDiff = Math.abs(new Date(timeValue).getTime() - now);
          return nextDiff < bestDiff ? index : bestIndex;
        }, 0);
        const aqi = Math.round(Number(aqiValues[closestIndex]));
        if (!Number.isFinite(aqi)) throw new Error("Air quality unavailable");
        const [label, className] = aqiLabel(aqi);
        const pm25 = Number(pm25Values[closestIndex]);
        const pmText = Number.isFinite(pm25) ? ` PM2.5 ${pm25.toFixed(1)} micrograms per cubic meter.` : "";
        setConditionCard(airCard, `AQI ${aqi}: ${label}`, `Open-Meteo air quality near this park.${pmText}`, className);
      })
      .catch(() => {
        setConditionCard(airCard, "Check air quality", "Air quality is temporarily unavailable here. Open the air quality source.", "condition-watch");
      });
  }

  if (roadsCard && roadUrl) {
    const link = roadsCard.querySelector("a");
    if (link) link.href = roadUrl;
  }
};

for (const dashboard of conditionsDashboards) {
  initConditionsDashboard(dashboard);
}

const renderOpenMeteoWeather = (lat, lng, hourlyEl, dailyEl) => {
  const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lng}&temperature_unit=fahrenheit&hourly=temperature_2m,weather_code&daily=temperature_2m_max,weather_code&forecast_days=7&timezone=auto`;
  return fetch(url)
    .then((response) => {
      if (!response.ok) throw new Error("Global forecast unavailable");
      return response.json();
    })
    .then((forecast) => {
      const hourlyTimes = forecast.hourly?.time || [];
      const hourlyTemps = forecast.hourly?.temperature_2m || [];
      const hourlyCodes = forecast.hourly?.weather_code || [];
      const dailyTimes = forecast.daily?.time || [];
      const dailyTemps = forecast.daily?.temperature_2m_max || [];
      const dailyCodes = forecast.daily?.weather_code || [];

      if (hourlyEl) {
        hourlyEl.replaceChildren(
          ...hourlyTimes.slice(0, 12).map((timeValue, index) => {
            const item = document.createElement("div");
            item.className = "hourly-item";
            const time = new Date(timeValue);
            const code = hourlyCodes[index];
            item.innerHTML = `<span>${time.toLocaleTimeString([], { hour: "numeric" })}</span><strong data-temp-f="${hourlyTemps[index]}">${displayTemp(hourlyTemps[index], currentWeatherUnit)}</strong><small>${weatherCodeText[code] || "Forecast"}</small>`;
            return item;
          })
        );
      }

      if (dailyEl) {
        dailyEl.replaceChildren(
          ...dailyTimes.slice(0, 7).map((dateValue, index) => {
            const item = document.createElement("div");
            item.className = "daily-item";
            const day = new Date(`${dateValue}T12:00:00`);
            const code = dailyCodes[index];
            item.innerHTML = `<strong>${day.toLocaleDateString([], { weekday: "long" })}</strong><span data-temp-f="${dailyTemps[index]}">${displayTemp(dailyTemps[index], currentWeatherUnit)}</span><p>${weatherCodeText[code] || "Forecast"}</p>`;
            return item;
          })
        );
      }
    });
};

if (weatherSection) {
  const lat = weatherSection.dataset.lat;
  const lng = weatherSection.dataset.lng;
  const hourlyEl = weatherSection.querySelector("[data-weather-hourly]");
  const dailyEl = weatherSection.querySelector("[data-weather-daily]");
  const unitButtons = Array.from(weatherSection.querySelectorAll("[data-weather-unit]"));

  const applyWeatherUnit = (unit) => {
    currentWeatherUnit = unit;
    localStorage.setItem("temperatureUnit", unit);
    for (const button of unitButtons) {
      const isActive = button.dataset.weatherUnit === unit;
      button.classList.toggle("active", isActive);
      button.setAttribute("aria-pressed", String(isActive));
    }
    weatherSection.querySelectorAll("[data-temp-f]").forEach((el) => {
      el.textContent = displayTemp(el.dataset.tempF, unit);
    });
  };

  for (const button of unitButtons) {
    button.addEventListener("click", () => applyWeatherUnit(button.dataset.weatherUnit || "F"));
  }

  applyWeatherUnit(currentWeatherUnit);

  fetch(`https://api.weather.gov/points/${lat},${lng}`)
    .then((response) => {
      if (!response.ok) throw new Error("Forecast point unavailable");
      return response.json();
    })
    .then((point) =>
      Promise.all([
        fetch(point.properties.forecastHourly).then((response) => response.json()),
        fetch(point.properties.forecast).then((response) => response.json()),
      ])
    )
    .then(([hourly, daily]) => {
      const hourlyItems = (hourly.properties?.periods || []).slice(0, 12);
      const dailyItems = (daily.properties?.periods || []).filter((period) => period.isDaytime).slice(0, 7);

      if (hourlyEl) {
        hourlyEl.replaceChildren(
          ...hourlyItems.map((period) => {
            const item = document.createElement("div");
            item.className = "hourly-item";
            const time = new Date(period.startTime);
            item.innerHTML = `<span>${time.toLocaleTimeString([], { hour: "numeric" })}</span><strong data-temp-f="${period.temperature}">${displayTemp(period.temperature, currentWeatherUnit)}</strong><small>${period.shortForecast}</small>`;
            return item;
          })
        );
      }

      if (dailyEl) {
        dailyEl.replaceChildren(
          ...dailyItems.map((period) => {
            const item = document.createElement("div");
            item.className = "daily-item";
            item.innerHTML = `<strong>${period.name}</strong><span data-temp-f="${period.temperature}">${displayTemp(period.temperature, currentWeatherUnit)}</span><p>${period.shortForecast}</p>`;
            return item;
          })
        );
      }
    })
    .catch(() =>
      renderOpenMeteoWeather(lat, lng, hourlyEl, dailyEl).catch(() => renderWeatherError("Weather is temporarily unavailable."))
    );
}
