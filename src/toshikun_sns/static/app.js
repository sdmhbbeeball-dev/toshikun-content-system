const labels = {
  shorts: "Shorts", x_posts: "X", instagram: "Instagram", line: "LINE",
  youtube_titles: "YouTubeタイトル", thumbnail_phrases: "サムネ文言"
};
const fieldLabels = { angle:"論点", hook:"フック", script:"台本", text:"本文", format:"形式", caption:"キャプション", slides:"スライド", evidence:"根拠となる原稿抜粋" };
const manuscript = document.querySelector("#manuscript");
const generate = document.querySelector("#generate");
const status = document.querySelector("#status");
const results = document.querySelector("#results");

generate.addEventListener("click", async () => {
  status.className = "";
  if (!manuscript.value.trim()) { status.textContent = "原稿を貼り付けてください。"; status.className = "error"; manuscript.focus(); return; }
  generate.disabled = true; generate.textContent = "生成しています…（1〜3分ほどかかります）"; status.textContent = "画面を閉じずにお待ちください。";
  try {
    const response = await fetch("/api/generate", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({manuscript:manuscript.value, access_password:document.querySelector("#access-password").value})});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "生成に失敗しました。");
    render(data); status.textContent = "生成が完了しました。"; results.hidden = false; results.scrollIntoView({behavior:"smooth"});
  } catch (error) { status.textContent = error.message; status.className = "error"; }
  finally { generate.disabled = false; generate.innerHTML = "<span>✨</span> SNSコンテンツを生成"; }
});

function render(data) {
  const tabs = document.querySelector("#tabs"); tabs.replaceChildren();
  const sections = Object.keys(labels);
  sections.forEach((key, index) => {
    const button = document.createElement("button"); button.textContent = `${labels[key]} (${(data.content[key] || []).length})`;
    button.className = index === 0 ? "active" : "";
    button.addEventListener("click", () => { tabs.querySelectorAll("button").forEach(b => b.classList.remove("active")); button.classList.add("active"); renderCards(key, data.content[key] || []); });
    tabs.append(button);
  });
  const summary = data.quality.summary;
  document.querySelector("#quality").textContent = `要確認：エラー ${summary.errors} / 警告 ${summary.warnings}`;
  renderCards(sections[0], data.content[sections[0]] || []);
}

function renderCards(section, items) {
  const cards = document.querySelector("#cards"); cards.replaceChildren();
  items.forEach((item, index) => {
    const card = document.createElement("article"); card.className = "card";
    const heading = document.createElement("h3"); heading.textContent = `${labels[section]} ${index + 1}`; card.append(heading);
    const copy = document.createElement("button"); copy.className = "copy"; copy.textContent = "コピー";
    copy.addEventListener("click", async () => { await navigator.clipboard.writeText(displayText(item)); copy.textContent = "コピー済み"; setTimeout(() => copy.textContent = "コピー", 1200); });
    heading.append(copy);
    Object.entries(item).forEach(([key, value]) => {
      const label = document.createElement("span"); label.className = "label"; label.textContent = fieldLabels[key] || key; card.append(label);
      const field = document.createElement("div"); field.className = "field"; field.textContent = Array.isArray(value) ? value.map((v,i) => `${i+1}. ${v}`).join("\n") : value; card.append(field);
    });
    cards.append(card);
  });
}
function displayText(item) { return Object.entries(item).filter(([key]) => key !== "evidence").map(([,value]) => Array.isArray(value) ? value.join("\n") : value).join("\n"); }
