const toggle = document.querySelector(".nav-toggle");
const nav = document.querySelector(".site-nav");
const recentNav = document.querySelector("#recent-parks");
const pageSlug = document.body.dataset.pageSlug;
const pageTitle = document.body.dataset.pageTitle;
const pageDepth = Number(document.body.dataset.pageDepth || "0");

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
]);

const getParkHref = (slug) =>
  noCameraParkSlugs.has(slug)
    ? `${pageDepth > 0 ? "" : "parks/"}${slug}.html`
    : `${nationalParkCamBaseUrl}/parks/${slug}.html`;

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
  search.addEventListener("input", () => {
    const query = search.value.trim().toLowerCase();
    for (const card of cards) {
      const title = card.dataset.title || "";
      card.hidden = query.length > 0 && !title.includes(query);
    }
    for (const button of mapButtons) {
      const title = button.dataset.title || "";
      button.hidden = query.length > 0 && !title.includes(query);
    }
  });
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
const webcamFrames = Array.from(document.querySelectorAll(".webcam-image-media[data-full-src]"));

if (webcamFrames.length) {
  const viewer = document.createElement("div");
  viewer.className = "image-viewer";
  viewer.hidden = true;
  viewer.innerHTML = `
    <button class="image-viewer-close" type="button" aria-label="Close larger webcam image">&times;</button>
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
    const title = frame.dataset.title || image?.alt || "Webcam image";
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
    viewerCaption.textContent = "This webcam image is temporarily unavailable.";
  });

  for (const frame of webcamFrames) {
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
            item.innerHTML = `<span>${time.toLocaleTimeString([], { hour: "numeric" })}</span><strong>${formatTemp(hourlyTemps[index], "F")}</strong><small>${weatherCodeText[code] || "Forecast"}</small>`;
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
            item.innerHTML = `<strong>${day.toLocaleDateString([], { weekday: "long" })}</strong><span>${formatTemp(dailyTemps[index], "F")}</span><p>${weatherCodeText[code] || "Forecast"}</p>`;
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
            item.innerHTML = `<span>${time.toLocaleTimeString([], { hour: "numeric" })}</span><strong>${formatTemp(period.temperature, period.temperatureUnit)}</strong><small>${period.shortForecast}</small>`;
            return item;
          })
        );
      }

      if (dailyEl) {
        dailyEl.replaceChildren(
          ...dailyItems.map((period) => {
            const item = document.createElement("div");
            item.className = "daily-item";
            item.innerHTML = `<strong>${period.name}</strong><span>${formatTemp(period.temperature, period.temperatureUnit)}</span><p>${period.shortForecast}</p>`;
            return item;
          })
        );
      }
    })
    .catch(() =>
      renderOpenMeteoWeather(lat, lng, hourlyEl, dailyEl).catch(() => renderWeatherError("Weather is temporarily unavailable."))
    );
}
