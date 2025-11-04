const API_BASE = "http://127.0.0.1:8000";
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

// === health ===
(async () => {
  try {
    const data = await getJSON(`${API_BASE}/health`);
    $("health").textContent = data.status === "ok" ? "OK" : "?"
  } catch {
    $("health").textContent = "API недоступен";
  }
})();

// === register ===
$("btn-register").onclick = async () => {
  $("reg-result").textContent = "";
  try {
    const username = $("reg-username").value.trim();
    const password = $("reg-password").value;
    const data = await postJSON(`${API_BASE}/auth/register`, { username, password });
    $("reg-result").textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    $("reg-result").textContent = e.toString();
  }
};

// === login ===
$("btn-login").onclick = async () => {
  try {
    const username = $("login-username").value.trim();
    const password = $("login-password").value;
    const data = await postJSON(`${API_BASE}/auth/login`, { username, password });
    token = data.access_token;
    localStorage.setItem("unimarket_token", token);
    $("token-preview").textContent = token.slice(0, 24) + "...";
    alert("Успешный логин!");
  } catch (e) {
    alert("Ошибка логина: " + e.toString());
  }
};

// === categories ===
async function loadCategoriesTo(selectEl) {
  const cats = await getJSON(`${API_BASE}/categories`);
  // очистка
  selectEl.innerHTML = "<option value=''>—без категории—</option>";
  for (const c of cats) {
    const opt = document.createElement("option");
    opt.value = c.id;
    opt.textContent = `${c.id}: ${c.name}`;
    selectEl.appendChild(opt);
  }
}

$("btn-add-category").onclick = async () => {
  const name = $("cat-name").value.trim();
  if (!name) return alert("Введите название категории");
  try {
    await postJSON(`${API_BASE}/categories`, { name });
    $("cat-name").value = "";
    await refreshCategories();
    alert("Категория добавлена");
  } catch (e) {
    alert("Ошибка: " + e.toString());
  }
};
$("btn-load-categories").onclick = async () => refreshCategories();

async function refreshCategories() {
  await loadCategoriesTo($("item-category"));
  await loadCategoriesTo($("filter-category"));
}
refreshCategories(); // при загрузке

// === items ===
$("btn-add-item").onclick = async () => {
  try {
    const name = $("item-name").value.trim();
    const price = parseFloat($("item-price").value);
    const description = $("item-desc").value.trim() || null;
    const category_id = $("item-category").value ? parseInt($("item-category").value) : null;
    if (!name || !(price > 0)) return alert("Название и положительная цена обязательны");
    await postJSON(`${API_BASE}/items`, { name, price, description, category_id });
    $("item-name").value = "";
    $("item-price").value = "";
    $("item-desc").value = "";
    $("item-category").value = "";
    await loadItems();
  } catch (e) {
    alert("Ошибка добавления товара: " + e.toString());
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
  const order = $("order").value;

  if (cat) params.set("category_id", cat);
  params.set("limit", limit);
  params.set("offset", offset);
  params.set("sort_by", sort_by);
  params.set("order", order);

  const page = await getJSON(`${API_BASE}/items?` + params.toString());
  $("items").innerHTML = page.items.map(
    it => `<div class="item">#${it.id} — <b>${it.name}</b> (${it.price}) — cat=${it.category_id ?? "—"}</div>`
  ).join("");
  // корректируем next/prev по факту:
  $("offset").value = page.offset;
}
loadItems();
