const API_BASE = "http://localhost";
let token = localStorage.getItem("unimarket_token") || null;

// === helpers ===
const $ = (id) => document.getElementById(id);
const authHeaders = () => token ? { "Authorization": `Bearer ${token}` } : {};
const jsonHeaders = () => ({ "Content-Type": "application/json", ...authHeaders() });

async function getJSON(url) {
  const r = await fetch(url, { headers: authHeaders() });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}
async function postJSON(url, body) {
  const r = await fetch(url, { method: "POST", headers: jsonHeaders(), body: JSON.stringify(body) });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

// === Cosmic Effects ===
function createStars() {
  const bg = $("star-bg");
  const count = 100;
  for (let i = 0; i < count; i++) {
    const star = document.createElement("div");
    star.className = "star";
    const xy = [Math.random() * 100, Math.random() * 100];
    const duration = Math.random() * 3 + 2;
    const size = Math.random() * 2 + 1;

    star.style.left = keyToCss(xy[0]);
    star.style.top = keyToCss(xy[1]);
    star.style.width = size + "px";
    star.style.height = size + "px";
    star.style.animationDuration = duration + "s";
    star.style.animationDelay = Math.random() * 5 + "s";
    bg.appendChild(star);
  }
}
const keyToCss = val => val + "%";

// === Tabs Logic ===
document.querySelectorAll(".nav-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    // Deactivate all
    document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(t => t.classList.remove("active"));

    // Activate current
    btn.classList.add("active");
    const tabId = btn.getAttribute("data-tab");
    $(tabId).classList.add("active");
  });
});

// === app logic ===

// Health & Init
(async () => {
  createStars();
  try {
    const data = await getJSON(`${API_BASE}/health`);
    $("health").textContent = data.status === "ok" ? "Online" : "Unstable";
  } catch {
    $("health").textContent = "Offline";
  }
  updateUserDisplay();
})();

function updateUserDisplay() {
  if (token) {
    $("user-display").textContent = "User (Logged In)";
    $("status").textContent = "Connected";
    $("status").style.color = "var(--neon-green)";
    $("avatar-icon").textContent = "👨‍🚀";
  } else {
    $("user-display").textContent = "Guest";
    $("status").textContent = "Disconnected";
    $("avatar-icon").textContent = "👽";
  }
}

// === register ===
$("btn-register").onclick = async () => {
  $("reg-result").textContent = "Processing...";
  try {
    const username = $("reg-username").value.trim();
    const password = $("reg-password").value;
    const data = await postJSON(`${API_BASE}/auth/register`, { username, password });
    $("reg-result").textContent = "Success: " + data.username;
    // Auto fill login?
  } catch (e) {
    $("reg-result").textContent = e.toString();
  }
};

// === login ===
$("btn-login").onclick = async () => {
  try {
    const username = $("login-username").value.trim();
    const password = $("login-password").value;

    // OAuth2 requires form-data, not JSON
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData
    });

    if (!response.ok) throw new Error(await response.text());
    const data = await response.json();

    token = data.access_token;
    localStorage.setItem("unimarket_token", token);
    $("token-preview").textContent = token.slice(0, 12) + "...";
    updateUserDisplay();
    alert("Welcome to the Nexus!");
  } catch (e) {
    alert("Access Denied: " + e.toString());
  }
};

// === categories ===
async function loadCategoriesTo(selectEl) {
  try {
    const cats = await getJSON(`${API_BASE}/categories`);
    selectEl.innerHTML = "<option value=''>— Select Category —</option>";
    for (const c of cats) {
      const opt = document.createElement("option");
      opt.value = c.id;
      opt.textContent = `${c.name}`;
      selectEl.appendChild(opt);
    }
  } catch (e) {
    console.error("Failed to load categories", e);
  }
}

$("btn-add-category").onclick = async () => {
  const name = $("cat-name").value.trim();
  if (!name) return alert("Name required");
  try {
    await postJSON(`${API_BASE}/categories`, { name });
    $("cat-name").value = "";
    await refreshCategories();
    alert("Category Injected");
  } catch (e) {
    alert("Error: " + e.toString());
  }
};
$("btn-load-categories").onclick = async () => refreshCategories();

async function refreshCategories() {
  await loadCategoriesTo($("item-category"));
  await loadCategoriesTo($("filter-category"));
}
refreshCategories(); // initial load

// === items ===
$("btn-add-item").onclick = async () => {
  try {
    const name = $("item-name").value.trim();
    const price = parseFloat($("item-price").value);
    const description = $("item-desc").value.trim() || null;
    const category_id = $("item-category").value ? parseInt($("item-category").value) : null;
    if (!name || !(price > 0)) return alert("Invalid Input");

    await postJSON(`${API_BASE}/items`, { name, price, description, category_id });

    // Clear form
    $("item-name").value = "";
    $("item-price").value = "";
    $("item-desc").value = "";

    await loadItems();
    alert("Item Fabricated");
  } catch (e) {
    alert("Fabrication Failed: " + e.toString());
  }
};

$("btn-load-items").onclick = () => loadItems();

$("btn-prev").onclick = () => {
  let offset = parseInt($("offset").value) || 0;
  const limit = parseInt($("limit").value) || 10;
  offset = Math.max(0, offset - limit);
  $("offset").value = String(offset);
  loadItems();
};
$("btn-next").onclick = () => {
  let offset = parseInt($("offset").value) || 0;
  const limit = parseInt($("limit").value) || 10;
  $("offset").value = String(offset + limit);
  loadItems();
};

async function loadItems() {
  const params = new URLSearchParams();
  const cat = $("filter-category").value;
  const limit = $("limit").value || "10";
  const offset = $("offset").value || "0";
  const sort_by = $("sort-by").value;
  // const order = $("order").value; // Removed from UI for simplicity, default asc

  if (cat) params.set("category_id", cat);
  params.set("limit", limit);
  params.set("offset", offset);
  params.set("sort_by", sort_by);
  // params.set("order", order);

  try {
    const page = await getJSON(`${API_BASE}/items?` + params.toString());
    $("items").innerHTML = page.items.map(
      it => `
        <div class="item-card">
            <div class="item-id">#${it.id}</div>
            <h4 style="margin:5px 0">${it.name}</h4>
            <div class="item-price">${it.price} Credits</div>
            <div style="font-size:0.8em; color:var(--text-dim)">${it.description || "No specs"}</div>
        </div>
        `
    ).join("");

    $("offset").value = page.offset;
  } catch (e) {
    console.error(e);
    $("items").innerHTML = `<div style="color:red">Transmission Error</div>`;
  }
}
loadItems();

