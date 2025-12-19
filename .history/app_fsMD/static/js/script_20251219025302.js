document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("img").forEach(img => {
    // Skip if explicitly set already
    if (img.hasAttribute("loading")) return;

    // Skip above-the-fold or critical images if you mark them
    if (img.classList.contains("no-lazy")) {
      img.loading = "eager";
      return;
    }

    // Default: lazy load everything else
    img.loading = "lazy";
    img.decoding = "async";
  });
});

document.addEventListener("DOMContentLoaded", () => {
  const scrollTopBtn = document.getElementById("scrollTopBtn");
  if (scrollTopBtn) {
    const SHOW_OFFSET = 200;

    const toggleScrollTopBtn = () => {
      if (window.scrollY > SHOW_OFFSET) scrollTopBtn.classList.add("show");
      else scrollTopBtn.classList.remove("show");
    };

    toggleScrollTopBtn();
    window.addEventListener("scroll", toggleScrollTopBtn);

    scrollTopBtn.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }
});

document.addEventListener("scroll", () => {
  const navbar = document.querySelector(".navbar-fsmd");
  if (!navbar) return;

  if (window.scrollY > 20) navbar.classList.remove("transparent");
  else navbar.classList.add("transparent");
});

document.addEventListener("DOMContentLoaded", () => {
  const img = document.querySelector(".hero-image");
  if (!img) return;

  let lastScrollY = window.scrollY || window.pageYOffset;
  let ticking = false;
  const SPEED = 0.05;

  const updateParallax = () => {
    const offset = lastScrollY * SPEED;
    img.style.transform = `translateY(${offset}px)`;
    ticking = false;
  };

  window.addEventListener("scroll", () => {
    lastScrollY = window.scrollY || window.pageYOffset;
    if (!ticking) {
      window.requestAnimationFrame(updateParallax);
      ticking = true;
    }
  });
});

function initScrollAnimations() {
  const elements = document.querySelectorAll(".scroll-animate");

  if (!("IntersectionObserver" in window)) {
    elements.forEach(el => el.classList.add("fade-play"));
    return;
  }

  const observer = new IntersectionObserver(
    (entries, obs) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add("fade-play");
          obs.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.2 }
  );

  elements.forEach(el => observer.observe(el));
}

window.addEventListener("load", () => {
  const loader = document.getElementById("global-loader");

  setTimeout(() => {
    if (loader) loader.classList.add("hidden");

    document.querySelectorAll(".fade-blocked").forEach(el => {
      el.classList.remove("fade-blocked");
    });

    initScrollAnimations();
  }, 1500);
});

document.addEventListener("DOMContentLoaded", () => {
  const items = document.querySelectorAll(".program-item");
  if (!items.length) return;

  items.forEach(item => {
    const bar = item.querySelector(".program-bar");
    const panelInner = item.querySelector(".accordion-anim");
    if (!bar || !panelInner) return;

    bar.addEventListener("click", () => {
      const isActive = item.classList.contains("active");
      const isVertical = window.matchMedia("(max-width: 992px)").matches;
      const enterDirectionClass = isVertical ? "fade-in-down" : "fade-in-left";

      items.forEach(i => {
        if (i.classList.contains("active")) {
          const inner = i.querySelector(".accordion-anim");
          if (inner) {
            inner.classList.remove("fade-in", "fade-in-up", "fade-in-down", "fade-in-left", "fade-in-right");
            inner.classList.add("fade-out");
          }
        }
      });

      setTimeout(() => {
        items.forEach(i => {
          i.classList.remove("active");
          const inner = i.querySelector(".accordion-anim");
          if (inner) {
            inner.classList.remove("fade-in", "fade-in-up", "fade-in-down", "fade-in-left", "fade-in-right", "fade-out");
            inner.style.animationDelay = "0s";
          }
        });

        if (!isActive) {
          item.classList.add("active");
          panelInner.style.animationDelay = "0.35s";

          panelInner.classList.remove("fade-in", "fade-in-up", "fade-in-down", "fade-in-left", "fade-in-right", "fade-out");
          void panelInner.offsetWidth;
          panelInner.classList.add("fade-in", enterDirectionClass);
        }
      }, 250);
    });
  });
});

document.addEventListener("DOMContentLoaded", () => {
  const sliders = document.querySelectorAll(".result-slider");
  if (!sliders.length) return;

  sliders.forEach(slider => {
    const handle = slider.querySelector(".result-slider-handle");
    const divider = slider.querySelector(".result-slider-divider");
    if (!handle || !divider) return;

    const initial = parseInt(slider.getAttribute("data-initial") || "50", 10);
    let isDragging = false;

    const setPositionFromClientX = (clientX) => {
      const rect = slider.getBoundingClientRect();
      let percent = ((clientX - rect.left) / rect.width) * 100;
      percent = Math.min(100, Math.max(0, percent));
      const pos = percent + "%";

      slider.style.setProperty("--reveal", pos);
      handle.style.left = pos;
      divider.style.left = pos;
    };

    const startDrag = (clientX) => {
      isDragging = true;
      slider.classList.add("is-dragging");
      setPositionFromClientX(clientX);
    };

    const onPointerMove = (e) => {
      if (!isDragging) return;
      let clientX;
      if (e.touches && e.touches.length) clientX = e.touches[0].clientX;
      else clientX = e.clientX;
      setPositionFromClientX(clientX);
    };

    const endDrag = () => {
      if (!isDragging) return;
      isDragging = false;
      slider.classList.remove("is-dragging");
    };

    const rect = slider.getBoundingClientRect();
    const initialX = rect.left + (initial / 100) * rect.width;
    setPositionFromClientX(initialX);

    handle.addEventListener("mousedown", (e) => {
      e.preventDefault();
      startDrag(e.clientX);
    });

    document.addEventListener("mousemove", onPointerMove);
    document.addEventListener("mouseup", endDrag);

    handle.addEventListener("touchstart", (e) => {
      e.preventDefault();
      if (!e.touches || !e.touches.length) return;
      startDrag(e.touches[0].clientX);
    }, { passive: false });

    document.addEventListener("touchmove", onPointerMove, { passive: false });
    document.addEventListener("touchend", endDrag);
    document.addEventListener("touchcancel", endDrag);
  });
});

document.addEventListener("DOMContentLoaded", () => {
  const filterButtons = document.querySelectorAll(".product-filter-btn[data-filter]");
  const productCards = Array.from(document.querySelectorAll(".product-card-wrapper[data-category]"));

  const toggleBtn = document.querySelector(".products-toggle-btn");
  const toggleLabel = toggleBtn ? toggleBtn.querySelector(".products-toggle-label") : null;

  if (!filterButtons.length || !productCards.length) return;

  const VISIBLE_LIMIT = 8;
  let currentFilter = "all";
  let showAllProducts = false;

  const applyFilter = (filter) => {
    currentFilter = filter;

    let visibleIndex = 0;
    let totalMatches = 0;

    productCards.forEach(card => {
      const categories = card.dataset.category.split(/\s+/).filter(Boolean);
      const matches = (filter === "all") || categories.includes(filter);

      card.classList.remove("product-card-animate");
      card.style.animationDelay = "0s";

      if (matches) {
        totalMatches++;
        const shouldShow = showAllProducts || visibleIndex < VISIBLE_LIMIT;

        if (shouldShow) {
          card.classList.remove("d-none");
          void card.offsetWidth;
          card.style.animationDelay = `${visibleIndex * 0.05}s`;
          card.classList.add("product-card-animate");
          visibleIndex += 1;
        } else {
          card.classList.add("d-none");
        }
      } else {
        card.classList.add("d-none");
      }
    });

    if (!toggleBtn || !toggleLabel) return;

    if (totalMatches > VISIBLE_LIMIT) {
      toggleBtn.classList.remove("d-none");
      toggleLabel.textContent = showAllProducts ? "Hide products" : "See more products";
    } else {
      toggleBtn.classList.add("d-none");
      showAllProducts = false;
    }
  };

  filterButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const filter = btn.getAttribute("data-filter");
      if (btn.disabled || btn.classList.contains("disabled")) return;

      showAllProducts = false;
      filterButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      applyFilter(filter);
    });
  });

  if (toggleBtn && toggleLabel) {
    toggleBtn.addEventListener("click", () => {
      showAllProducts = !showAllProducts;
      applyFilter(currentFilter);
    });
  }

  applyFilter("all");
});

document.addEventListener("DOMContentLoaded", () => {
  const carouselEl = document.getElementById("feedbackCarousel");
  if (!carouselEl || typeof bootstrap === "undefined") return;

  const carousel = bootstrap.Carousel.getOrCreateInstance(carouselEl, {
    ride: false,
    touch: true,
    interval: false,
    wrap: true
  });

  const thumbsWrap = document.querySelector(".feedback-thumbs");
  if (!thumbsWrap) return;

  if (!thumbsWrap.dataset.duped) {
    const originals = Array.from(thumbsWrap.querySelectorAll(".feedback-thumb"));
    originals.forEach(btn => {
      const clone = btn.cloneNode(true);
      clone.dataset.clone = "1";
      thumbsWrap.appendChild(clone);
    });
    thumbsWrap.dataset.duped = "1";
  }

  const getAllThumbs = () => Array.from(document.querySelectorAll(".feedback-thumb"));

  const setActiveThumb = (idx) => {
    const allThumbs = getAllThumbs();
    allThumbs.forEach(t => t.classList.remove("is-active"));

    const matches = allThumbs.filter(t => Number(t.getAttribute("data-bs-slide-to")) === idx);
    matches.forEach(t => t.classList.add("is-active"));

    const primary = matches.find(t => !t.dataset.clone) || matches[0];
    primary?.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
  };

  getAllThumbs().forEach((btn) => {
    btn.addEventListener("click", () => {
      const i = Number(btn.getAttribute("data-bs-slide-to"));
      setActiveThumb(i);
    });
  });

  carouselEl.addEventListener("slid.bs.carousel", (e) => {
    setActiveThumb(e.to);
  });

  let startX = 0, startY = 0, down = false;
  const threshold = 40, restraint = 60;

  carouselEl.addEventListener("pointerdown", (e) => {
    down = true;
    startX = e.clientX;
    startY = e.clientY;
  });

  carouselEl.addEventListener("pointerup", (e) => {
    if (!down) return;
    down = false;

    const dx = e.clientX - startX;
    const dy = e.clientY - startY;

    if (Math.abs(dx) >= threshold && Math.abs(dy) <= restraint) {
      if (dx < 0) carousel.next();
      else carousel.prev();
    }
  });

  carouselEl.addEventListener("pointercancel", () => { down = false; });
  carouselEl.addEventListener("pointerleave", () => { down = false; });

  const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (prefersReduced) return;

  thumbsWrap.classList.add("is-auto");

  let loopPoint = 0;
  const computeLoopPoint = () => {
    loopPoint = thumbsWrap.scrollWidth / 2;
  };

  computeLoopPoint();
  window.addEventListener("resize", computeLoopPoint);

  const speedPxPerSec = 22;
  let paused = false;
  let lastTime = 0;

  const tick = (t) => {
    if (!lastTime) lastTime = t;
    const dt = (t - lastTime) / 1000;
    lastTime = t;

    if (!paused) {
      if (loopPoint <= 0) computeLoopPoint();

      thumbsWrap.scrollLeft += speedPxPerSec * dt;

      if (thumbsWrap.scrollLeft >= loopPoint) {
        thumbsWrap.scrollLeft -= loopPoint;
      }
    }

    requestAnimationFrame(tick);
  };

  requestAnimationFrame(tick);

  const pause = () => { paused = true; };
  const resume = () => { paused = false; lastTime = 0; };

  thumbsWrap.addEventListener("mouseenter", pause);
  thumbsWrap.addEventListener("mouseleave", resume);

  thumbsWrap.addEventListener("pointerdown", pause, { passive: true });
  thumbsWrap.addEventListener("pointerup", () => setTimeout(resume, 250), { passive: true });
  thumbsWrap.addEventListener("pointercancel", () => setTimeout(resume, 250), { passive: true });

  document.addEventListener("visibilitychange", () => {
    if (document.hidden) pause();
    else resume();
  });
});

document.addEventListener("DOMContentLoaded", () => {
  const list = document.getElementById("blogPostsDragList");
  const featuredImg = document.getElementById("blogFeaturedImg");
  const featuredLink = document.getElementById("blogFeaturedLink");
  const featuredWrap = featuredImg ? featuredImg.closest(".blog-feature-visual") : null;

  if (!list || !featuredImg || !featuredLink || !featuredWrap) return;

  const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const items = Array.from(list.querySelectorAll(".blog-post-row"));

  const swapFeatured = (src, href) => {
    if (!src) return;
    featuredWrap.classList.add("is-swapping");
    setTimeout(() => {
      featuredImg.src = src;
      if (href) featuredLink.href = href;
      featuredWrap.classList.remove("is-swapping");
    }, prefersReduced ? 0 : 140);
  };

  const setActive = (el) => {
    items.forEach(i => i.classList.remove("is-active"));
    if (el) el.classList.add("is-active");
  };

  const first = items[0];
  if (first) {
    setActive(first);
    swapFeatured(first.getAttribute("data-img"), first.getAttribute("href"));
  }

  items.forEach((item) => {
    const img = item.getAttribute("data-img");
    const href = item.getAttribute("href");

    item.addEventListener("mouseenter", () => {
      setActive(item);
      swapFeatured(img, href);
    });

    item.addEventListener("focusin", () => {
      setActive(item);
      swapFeatured(img, href);
    });

    item.addEventListener("dragstart", (e) => e.preventDefault());
    item.querySelectorAll("img").forEach(imgEl => imgEl.addEventListener("dragstart", (e) => e.preventDefault()));
  });

  let activePointer = null;
  let startY = 0;
  let startTop = 0;
  let dragged = false;

  const onDown = (e) => {
    if (e.button !== undefined && e.button !== 0) return;
    activePointer = e.pointerId ?? "mouse";
    dragged = false;
    startY = e.clientY;
    startTop = list.scrollTop;
    list.classList.add("is-dragging");
    if (list.setPointerCapture && e.pointerId !== undefined) list.setPointerCapture(e.pointerId);
    e.preventDefault();
  };

  const onMove = (e) => {
    if (activePointer === null) return;
    if (e.pointerId !== undefined && activePointer !== e.pointerId) return;

    const dy = e.clientY - startY;
    if (Math.abs(dy) > 3) dragged = true;
    list.scrollTop = startTop - dy;
  };

  const onUp = (e) => {
    if (activePointer === null) return;
    if (e && e.pointerId !== undefined && activePointer !== e.pointerId) return;

    activePointer = null;
    list.classList.remove("is-dragging");
  };

  list.addEventListener("pointerdown", onDown, { passive: false });
  window.addEventListener("pointermove", onMove, { passive: true });
  window.addEventListener("pointerup", onUp, { passive: true });
  window.addEventListener("pointercancel", onUp, { passive: true });

  list.addEventListener("click", (e) => {
    if (!dragged) return;
    e.preventDefault();
    e.stopPropagation();
  }, true);
});

document.addEventListener("DOMContentLoaded", () => {
  const filtersEl = document.getElementById("blogFilters");
  const postBtns = Array.from(document.querySelectorAll(".blog-post-btn"));

  const featuredImg = document.getElementById("featuredImg");
  const featuredBadge = document.getElementById("featuredBadge");
  const featuredDate = document.getElementById("featuredDate");
  const featuredRead = document.getElementById("featuredRead");
  const featuredTitle = document.getElementById("featuredTitle");
  const featuredDesc = document.getElementById("featuredDesc");
  const featuredBullets = document.getElementById("featuredBullets");

  if (!filtersEl || !postBtns.length || !featuredImg || !featuredBadge || !featuredDate || !featuredRead || !featuredTitle || !featuredDesc || !featuredBullets) {
    return;
  }

  const filterBtns = Array.from(filtersEl.querySelectorAll("button[data-filter]"));

  const setActiveCard = (btn) => {
    postBtns.forEach(b => {
      b.classList.remove("is-active");
      const card = b.querySelector(".blog-post-card");
      if (card) {
        card.classList.remove("border-primary", "border-2");
        if (!card.classList.contains("border")) card.classList.add("border");
      }
    });

    if (btn) {
      btn.classList.add("is-active");
      const card = btn.querySelector(".blog-post-card");
      if (card) card.classList.add("border-primary", "border-2");
    }
  };

  const setFeaturedFrom = (btn) => {
    if (!btn) return;

    setActiveCard(btn);

    featuredImg.src = btn.dataset.img || featuredImg.src;
    featuredImg.alt = btn.dataset.title || "Featured blog";

    featuredBadge.innerHTML = btn.dataset.badge || "";
    featuredDate.textContent = btn.dataset.date || "";
    featuredRead.textContent = btn.dataset.read || "";

    featuredTitle.textContent = btn.dataset.title || "";
    featuredDesc.textContent = btn.dataset.desc || "";

    const bullets = [btn.dataset.b1, btn.dataset.b2, btn.dataset.b3].filter(Boolean);
    featuredBullets.innerHTML = bullets.map(t => `
      <li class="d-flex gap-2 align-items-start">
        <i class="fa-solid fa-circle-check text-primary-accent mt-1"></i>
        <span class="text-body-sm">${t}</span>
      </li>
    `).join("");
  };

  const applyFilter = (topic) => {
    let firstVisible = null;

    postBtns.forEach(btn => {
      const match = (topic === "all") || (btn.dataset.topic === topic);
      btn.classList.toggle("d-none", !match);
      if (match && !firstVisible) firstVisible = btn;
    });

    const active = document.querySelector(".blog-post-btn.is-active");
    if (!active || active.classList.contains("d-none")) {
      setFeaturedFrom(firstVisible || postBtns[0]);
    }
  };

  // Click post -> preview
  postBtns.forEach(btn => {
    btn.addEventListener("click", () => setFeaturedFrom(btn));
    btn.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        setFeaturedFrom(btn);
      }
    });
  });

  // Filters -> event delegation (works even if icon/text clicked)
  filtersEl.addEventListener("click", (e) => {
    // If the user was dragging the filters bar, ignore the click
    if (filtersEl.dataset.dragged === "1") return;

    const btn = e.target.closest("button[data-filter]");
    if (!btn || !filtersEl.contains(btn)) return;

    filterBtns.forEach(b => {
      b.classList.remove("active");
      b.setAttribute("aria-pressed", "false");
    });

    btn.classList.add("active");
    btn.setAttribute("aria-pressed", "true");

    applyFilter(btn.dataset.filter || "all");
  });

  // Drag-to-scroll for filter bar (without breaking clicks)
  let isDown = false;
  let startX = 0;
  let startLeft = 0;
  let dragged = false;

  const onDown = (e) => {
    isDown = true;
    dragged = false;
    filtersEl.dataset.dragged = "0";
    filtersEl.classList.add("is-dragging");
    startX = e.clientX;
    startLeft = filtersEl.scrollLeft;
  };

  const onMove = (e) => {
    if (!isDown) return;
    const dx = e.clientX - startX;
    if (Math.abs(dx) > 4) {
      dragged = true;
      filtersEl.dataset.dragged = "1";
    }
    filtersEl.scrollLeft = startLeft - dx;
  };

  const onUp = () => {
    isDown = false;
    filtersEl.classList.remove("is-dragging");
    // allow normal clicks again after a short moment
    if (dragged) setTimeout(() => (filtersEl.dataset.dragged = "0"), 150);
  };

  filtersEl.addEventListener("pointerdown", onDown, { passive: true });
  window.addEventListener("pointermove", onMove, { passive: true });
  window.addEventListener("pointerup", onUp, { passive: true });
  window.addEventListener("pointercancel", onUp, { passive: true });

  // init
  const initial = document.querySelector(".blog-post-btn.is-active") || postBtns[0];
  setFeaturedFrom(initial);
  applyFilter("all");
});

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("article").forEach((card) => {
    const shortEl = card.querySelector(".js-desc-short");
    const ellipsis = card.querySelector(".js-desc-ellipsis");
    const moreBtn = card.querySelector(".js-desc-more");
    const hideBtn = card.querySelector(".js-desc-hide");

    const wrap = card.querySelector(".js-desc-wrap");
    const inner = card.querySelector(".desc-expand-inner");

    if (!shortEl || !wrap || !inner || !moreBtn || !hideBtn) return;

    const shortLine = shortEl.closest("p");

    const playIn = (el) => {
      el.classList.remove("fade-out-down", "fade-blocked");
      el.classList.add("fade-in", "fade-in-up", "fade-play");
    };

    const playOut = (el) => {
      el.classList.remove("fade-in", "fade-in-up", "fade-play");
      el.classList.add("fade-out-down");
    };

    const open = () => {
      if (wrap.dataset.open === "1") return;
      wrap.dataset.open = "1";
      moreBtn.setAttribute("aria-expanded", "true");

      // fade out the truncated line
      if (shortLine) playOut(shortLine);

      // after fade-out starts, expand + fade-in full
      setTimeout(() => {
        shortEl.classList.add("d-none");
        ellipsis?.classList.add("d-none");
        moreBtn.classList.add("d-none");
        hideBtn.classList.remove("d-none");

        // prepare inner to fade in
        inner.classList.add("fade-blocked");
        wrap.style.height = inner.scrollHeight + "px";

        // trigger animation (remove blocked, then play)
        requestAnimationFrame(() => {
          inner.classList.remove("fade-blocked");
          playIn(inner);
          wrap.style.height = inner.scrollHeight + "px";
        });
      }, 220);
    };

    const close = () => {
      if (wrap.dataset.open !== "1") return;
      wrap.dataset.open = "0";
      moreBtn.setAttribute("aria-expanded", "false");

      // fade out expanded content
      playOut(inner);

      // collapse height
      wrap.style.height = inner.scrollHeight + "px";
      requestAnimationFrame(() => {
        wrap.style.height = "0px";
      });

      // after collapse, show truncated line again and fade it in
      setTimeout(() => {
        hideBtn.classList.add("d-none");
        shortEl.classList.remove("d-none");
        ellipsis?.classList.remove("d-none");
        moreBtn.classList.remove("d-none");

        // reset short line animation + play in
        if (shortLine) {
          shortLine.classList.add("fade-blocked");
          requestAnimationFrame(() => {
            shortLine.classList.remove("fade-blocked");
            playIn(shortLine);
          });
        }
      }, 480);
    };

    moreBtn.addEventListener("click", open);
    hideBtn.addEventListener("click", close);
  });
});

document.addEventListener("DOMContentLoaded", () => {
  const unitEl = document.getElementById("unitPrice");
  const totalEl = document.getElementById("totalPrice");

  const qtyInput = document.getElementById("qtyInput");
  const qtyMinus = document.getElementById("qtyMinus");
  const qtyPlus  = document.getElementById("qtyPlus");

  if (unitEl && totalEl && qtyInput && qtyMinus && qtyPlus) {
    const unit = Number(unitEl.dataset.unit || "0");
    const minQty = Number(qtyInput.min || "1");
    const maxQty = Number(qtyInput.dataset.max || qtyInput.max || "999999"); // stock cap

    const fmt = (n) => (Math.round(n * 100) / 100).toFixed(2);

    const updateButtons = (q) => {
      qtyMinus.disabled = q <= minQty;
      qtyPlus.disabled = (maxQty > 0) ? (q >= maxQty) : false;
    };

    const recalc = () => {
      const q = Number(qtyInput.value || minQty);
      totalEl.textContent = fmt(unit * q);
    };

    const clampAndSet = (value) => {
      let q = parseInt(value, 10);
      if (Number.isNaN(q)) q = minQty;

      q = Math.max(minQty, q);
      if (maxQty > 0) q = Math.min(maxQty, q);

      qtyInput.value = q;
      updateButtons(q);
      recalc();
    };

    qtyMinus.addEventListener("click", () => clampAndSet(Number(qtyInput.value || minQty) - 1));
    qtyPlus.addEventListener("click",  () => clampAndSet(Number(qtyInput.value || minQty) + 1));

    qtyInput.addEventListener("input", () => clampAndSet(qtyInput.value));
    qtyInput.addEventListener("blur",  () => clampAndSet(qtyInput.value));

    clampAndSet(qtyInput.value);
  }

  // thumbnail swap (now uses the id)
  document.querySelectorAll(".product-thumb-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const full = btn.getAttribute("data-full");
      const main = document.getElementById("mainProductImage");
      if (full && main) main.src = full;
    });
  });
});




// =========================
// CART (add + side cart controls)
// =========================
(function(){
  const d = document;

  function getCookie(name){
    const m = d.cookie.match("(^|;)\\s*"+name+"\\s*=\\s*([^;]+)");
    return m ? m.pop() : "";
  }

  // --- Locale/Currency formatting (with commas + symbol) ---
  let currencyFormatter = null;

  function makeCurrencyFormatter(){
    const routesEl = d.getElementById("cartRoutes");

    // Pick locale + currency from data attributes if provided
    const locale =
      (routesEl && routesEl.dataset.locale) ||
      navigator.language ||
      "en-US";

    const currency =
      (routesEl && routesEl.dataset.currency) ||
      "USD";

    return new Intl.NumberFormat(locale, {
      style: "currency",
      currency: currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  }

  function toNumber(v){
    // Accept: "1000", "1,000.00", "$1,000.00", "₱1,000.00"
    const s = String(v ?? "0");
    const cleaned = s.replace(/[^0-9.\-]/g, ""); // keep digits, dot, minus
    const n = Number(cleaned);
    return Number.isFinite(n) ? n : 0;
  }

  function money(v){
    if(!currencyFormatter) currencyFormatter = makeCurrencyFormatter();
    return currencyFormatter.format(toNumber(v));
  }

  function emptyStateHTML(){
    return `
      <div class="cart-empty-state text-center">
        <div class="icon-button icon-button--gradient-border mx-auto mb-2" style="width:54px;height:54px;">
          <i class="fa-solid fa-cart-shopping"></i>
        </div>
        <div class="fw-semibold">Your cart is empty</div>
        <div class="text-body-sm text-muted">Add an item to get started.</div>
      </div>
    `;
  }

  function updateCartBadges(totalQty){
    const qty = parseInt(totalQty, 10) || 0;
    d.querySelectorAll(".cart-badge").forEach(b=>{
      b.textContent = qty;
      qty > 0 ? b.classList.remove("is-hidden") : b.classList.add("is-hidden");
      b.classList.remove("pop"); void b.offsetWidth; b.classList.add("pop");
    });
  }

  function renderCart(payload){
    const wrap = d.getElementById("cartContent");
    const totalEl = d.getElementById("cartTotal");

    if(totalEl) totalEl.textContent = money(payload.total_price);
    updateCartBadges(payload.total_qty);

    if(!wrap) return;

    if(!payload.items || !payload.items.length){
      wrap.innerHTML = emptyStateHTML();
      return;
    }

    wrap.innerHTML = payload.items.map(it=>{
      const rx = it.requires_prescription
        ? `<span class="badge rounded-pill bg-warning-subtle text-warning-emphasis ms-2">Prescription</span>`
        : it.requires_consultation
          ? `<span class="badge rounded-pill bg-info-subtle text-info-emphasis ms-2">Consultation</span>`
          : ``;

      const stock = (typeof it.stock === "number" && it.stock > 0) ? it.stock : 999999;
      const decDisabled = it.qty <= 1 ? "disabled" : "";
      const incDisabled = it.qty >= stock ? "disabled" : "";

      return `
        <div class="bg-white border rounded-4 shadow-sm p-3">
          <div class="d-flex gap-3 align-items-start">
            <div class="ratio ratio-1x1 rounded-3 overflow-hidden bg-muted border flex-shrink-0" style="width:64px;">
              ${it.image ? `<img src="${it.image}" class="w-100 h-100 object-fit-cover" alt="">` : ``}
            </div>

            <div class="flex-grow-1">
              <div class="d-flex align-items-start justify-content-between gap-2">
                <div>
                  <div class="fw-semibold">${it.name}${rx}</div>
                  <div class="text-caption-sm text-muted">${money(it.unit_price)} each</div>
                </div>

                <button class="icon-button icon-button--gradient-border"
                        type="button"
                        aria-label="Remove item"
                        data-action="remove"
                        data-product="${it.id}"
                        style="width:40px;height:40px;">
                  <i class="fa-solid fa-trash"></i>
                </button>
              </div>

              <div class="d-flex align-items-center justify-content-between gap-2 mt-3">
                <div class="input-group input-group-sm" style="max-width:160px;">
                  <button class="btn btn-outline-secondary"
                          type="button"
                          data-action="dec"
                          data-product="${it.id}"
                          ${decDisabled}
                          aria-label="Decrease quantity">
                    <i class="fa-solid fa-minus"></i>
                  </button>

                  <input class="form-control text-center"
                         type="number"
                         min="1"
                         max="${stock}"
                         value="${it.qty}"
                         inputmode="numeric"
                         autocomplete="off"
                         data-action="qty"
                         data-product="${it.id}">

                  <button class="btn btn-outline-secondary"
                          type="button"
                          data-action="inc"
                          data-product="${it.id}"
                          ${incDisabled}
                          aria-label="Increase quantity">
                    <i class="fa-solid fa-plus"></i>
                  </button>
                </div>

                <div class="fw-semibold">${money(it.line_total)}</div>
              </div>
            </div>
          </div>
        </div>
      `;
    }).join("");
  }

  async function getJSON(url){
    if(!url) return null;
    const res = await fetch(url, { headers: { "X-Requested-With":"XMLHttpRequest" } });
    return await res.json().catch(()=>null);
  }

  async function postAction(url, body){
    if(!url){
      console.warn("Cart URL missing. Check #cartRoutes data-* attributes.");
      return null;
    }
    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type":"application/x-www-form-urlencoded",
        "X-CSRFToken": getCookie("csrftoken"),
        "X-Requested-With":"XMLHttpRequest"
      },
      body: new URLSearchParams(body)
    });
    return await res.json().catch(()=>null);
  }

  d.addEventListener("DOMContentLoaded", async ()=>{
    const routesEl = d.getElementById("cartRoutes");
    if(!routesEl){
      console.warn("Missing #cartRoutes in base.html");
      return;
    }

    // Build formatter now (so it respects data-locale/data-currency)
    currencyFormatter = makeCurrencyFormatter();

    // ✅ Remove hardcoded "$" that is before <span id="cartTotal">
    const totalEl = d.getElementById("cartTotal");
    if(totalEl && totalEl.parentElement){
      totalEl.parentElement.childNodes.forEach(n=>{
        if(n.nodeType === Node.TEXT_NODE && n.textContent.trim() !== ""){
          n.textContent = ""; // removes "$"
        }
      });
    }

    const routes = {
      summary: routesEl.dataset.cartSummaryUrl,
      add: routesEl.dataset.cartAddUrl,
      update: routesEl.dataset.cartUpdateUrl,
      remove: routesEl.dataset.cartRemoveUrl
    };

    // Initial badge + cart render
    const init = await getJSON(routes.summary);
    if(init && init.ok) renderCart(init);

    // Refresh when opening offcanvas
    const off = d.getElementById("cartOffcanvas");
    if(off && window.bootstrap){
      off.addEventListener("shown.bs.offcanvas", async ()=>{
        const data = await getJSON(routes.summary);
        if(data && data.ok) renderCart(data);
      });
    }

    // ✅ ADD TO CART (product detail button)
    const addBtn = d.getElementById("addToCartBtn");
    if(addBtn){
      addBtn.addEventListener("click", async ()=>{
        const productId = addBtn.dataset.product;
        const qty = d.getElementById("qtyInput")?.value || "1";

        if(!productId){
          console.warn("Missing data-product on #addToCartBtn");
          return;
        }

        addBtn.disabled = true;

        try{
          const data = await postAction(routes.add || addBtn.dataset.cartAddUrl, {
            product_id: productId,
            qty: qty
          });

          if(!data || !data.ok){
            alert((data && data.error) ? data.error : "Failed to add to cart");
            return;
          }

          // Refresh full cart (items + totals) after add
          const sum = await getJSON(routes.summary || addBtn.dataset.cartSummaryUrl);
          if(sum && sum.ok) renderCart(sum);

          // If you WANT to auto-open the side cart, uncomment:
          // if(off && window.bootstrap) bootstrap.Offcanvas.getOrCreateInstance(off).show();

        } finally {
          addBtn.disabled = false;
        }
      });
    }

    // Side cart controls (remove / inc / dec)
    const wrap = d.getElementById("cartContent");
    if(!wrap) return;

    wrap.addEventListener("click", async (e)=>{
      const btn = e.target.closest("[data-action]");
      if(!btn) return;

      const action = btn.dataset.action;
      const productId = btn.dataset.product;
      if(!productId) return;

      btn.disabled = true;

      try{
        if(action === "remove"){
          const data = await postAction(routes.remove, { product_id: productId });
          if(data && data.ok) renderCart(data);
          return;
        }

        if(action === "inc" || action === "dec"){
          const input = wrap.querySelector(`input[data-action="qty"][data-product="${productId}"]`);
          if(!input) return;

          let q = parseInt(input.value, 10) || 1;
          q = action === "inc" ? q + 1 : q - 1;
          q = Math.max(1, q);

          const max = parseInt(input.getAttribute("max"), 10);
          if(!Number.isNaN(max)) q = Math.min(q, max);

          const data = await postAction(routes.update, { product_id: productId, qty: q });
          if(data && data.ok) renderCart(data);
        }
      } finally {
        btn.disabled = false;
      }
    });

    // Manual qty change
    wrap.addEventListener("change", async (e)=>{
      const input = e.target.closest('input[data-action="qty"]');
      if(!input) return;

      const productId = input.dataset.product;
      let q = parseInt(input.value, 10) || 1;
      q = Math.max(1, q);

      const max = parseInt(input.getAttribute("max"), 10);
      if(!Number.isNaN(max)) q = Math.min(q, max);

      const data = await postAction(routes.update, { product_id: productId, qty: q });
      if(data && data.ok) renderCart(data);
    });
  });
})();

document.addEventListener("DOMContentLoaded", () => {
  const panel = document.getElementById("fsmdSidebarPanel");
  if (!panel) return;

  panel.addEventListener("shown.bs.offcanvas", () => {
    panel.querySelectorAll(".fade-blocked").forEach(el => el.classList.remove("fade-blocked"));
  });
});
