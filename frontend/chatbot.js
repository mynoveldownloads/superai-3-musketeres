/**
 * chatbot.js — Injects a floating chat bubble + popup window into any page.
 * Include with: <script src="chatbot.js"></script> before </body>
 * The green chat bubble already in each page should call openChat() on click.
 */

(function () {

  /* ── Inject styles ─────────────────────────────────────────────────── */
  const style = document.createElement("style");
  style.textContent = `
    /* Overlay backdrop */
    #chatOverlay {
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.25);
      z-index: 2000;
      align-items: flex-end;
      justify-content: flex-end;
      padding: 0 24px 90px 0;
    }
    #chatOverlay.open { display: flex; }

    /* Chat window */
    #chatWindow {
      width: 480px;
      height: min(680px, calc(100vh - 110px));
      background: white;
      border-radius: 22px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.22);
      display: flex;
      flex-direction: column;
      overflow: hidden;
      animation: chatSlideUp 0.22s ease;
    }

    @keyframes chatSlideUp {
      from { opacity: 0; transform: translateY(24px); }
      to   { opacity: 1; transform: translateY(0); }
    }

    /* Header */
    #chatWindow .cw-header {
      background: linear-gradient(135deg, #f472b6, #a855f7);
      padding: 16px 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-shrink: 0;
    }
    #chatWindow .cw-title {
      font-size: 18px;
      font-weight: 700;
      font-style: italic;
      color: white;
    }
    #chatWindow .cw-header-btns {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    #chatWindow .cw-dots {
      background: none; border: none; cursor: pointer;
      display: flex; gap: 3px; align-items: center; padding: 4px;
    }
    #chatWindow .cw-dots span {
      width: 5px; height: 5px; background: white;
      border-radius: 50%; display: block;
    }
    #chatWindow .cw-close {
      background: none; border: none; color: white;
      font-size: 22px; cursor: pointer; line-height: 1; padding: 2px 4px;
    }
    #chatWindow .cw-close:hover { opacity: 0.75; }

    /* Messages */
    #chatMessages {
      flex: 1;
      overflow-y: auto;
      padding: 14px 14px;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    #chatMessages::-webkit-scrollbar { width: 4px; }
    #chatMessages::-webkit-scrollbar-thumb { background: #e5e7eb; border-radius: 4px; }

    .cw-msg {
      max-width: 75%;
      padding: 10px 14px;
      border-radius: 16px;
      font-size: 14px;
      line-height: 1.55;
      word-break: break-word;
    }
    .cw-msg img {
      max-width: 100%;
      border-radius: 10px;
      margin-top: 6px;
      display: block;
    }
    .cw-msg.bot {
      background: #f3f4f6; color: #111827;
      align-self: flex-start; border-bottom-left-radius: 4px;
    }
    .cw-msg.user {
      background: linear-gradient(135deg, #f472b6, #a855f7);
      color: white; align-self: flex-end; border-bottom-right-radius: 4px;
    }
    .cw-time {
      font-size: 10px; color: #9ca3af; margin-top: 1px;
    }
    .cw-time.right { align-self: flex-end; }
    .cw-time.left  { align-self: flex-start; }

    /* Typing indicator */
    #cwTyping {
      display: none;
      align-self: flex-start;
      background: #f3f4f6;
      border-radius: 16px;
      border-bottom-left-radius: 4px;
      padding: 10px 14px;
      gap: 5px;
      align-items: center;
    }
    #cwTyping.active { display: flex; }
    #cwTyping span {
      width: 6px; height: 6px; background: #a855f7;
      border-radius: 50%;
      animation: cwBounce 1.2s infinite;
    }
    #cwTyping span:nth-child(2) { animation-delay: 0.2s; }
    #cwTyping span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes cwBounce {
      0%,60%,100% { transform: translateY(0); }
      30%          { transform: translateY(-6px); }
    }

    /* Divider */
    .cw-divider { height: 1px; background: #f3f4f6; flex-shrink: 0; }

    /* Input row */
    .cw-input-row {
      padding: 10px 12px;
      display: flex; align-items: center; gap: 8px; flex-shrink: 0;
    }
    #cwInput {
      flex: 1; padding: 9px 14px;
      border: 1.5px solid #e5e7eb; border-radius: 999px;
      font-size: 13.5px; outline: none; color: #111827; background: #fafafa;
    }
    #cwInput::placeholder { color: #9ca3af; }
    #cwInput:focus {
      border-color: #a855f7;
      box-shadow: 0 0 0 3px rgba(168,85,247,0.12);
    }
    #cwSendBtn {
      width: 34px; height: 34px; border: none; border-radius: 50%;
      background: linear-gradient(135deg, #f472b6, #a855f7);
      color: white; font-size: 15px; cursor: pointer;
      display: flex; align-items: center; justify-content: center;
      flex-shrink: 0; transition: opacity 0.2s;
    }
    #cwSendBtn:hover { opacity: 0.85; }
  `;
  document.head.appendChild(style);

  /* ── Inject HTML ───────────────────────────────────────────────────── */
  const overlay = document.createElement("div");
  overlay.id = "chatOverlay";
  overlay.innerHTML = `
    <div id="chatWindow">
      <div class="cw-header">
        <span class="cw-title">Chat with us</span>
        <div class="cw-header-btns">
          <button class="cw-dots" title="Options">
            <span></span><span></span><span></span>
          </button>
          <button class="cw-close" id="cwCloseBtn" title="Close">×</button>
        </div>
      </div>

      <div id="chatMessages">
        <div class="cw-msg bot">👋 Hi! I'm the Musketeers Mart assistant. How can I help you today?</div>
        <div class="cw-time left">Just now</div>
        <div id="cwTyping"><span></span><span></span><span></span></div>
      </div>

      <div class="cw-divider"></div>

      <div class="cw-input-row">
        <input type="text" id="cwInput" placeholder="Type a message..." autocomplete="off" />
        <button id="cwSendBtn" title="Send">&#9658;</button>
      </div>
    </div>
  `;
  document.body.appendChild(overlay);

  /* ── Logic ─────────────────────────────────────────────────────────── */
  const messagesEl = document.getElementById("chatMessages");
  const inputEl    = document.getElementById("cwInput");
  const typingEl   = document.getElementById("cwTyping");

  const AGENT_URL  = "http://127.0.0.1:5000/chat";
  const SESSION_ID = crypto.randomUUID(); // unique per page load

  function timeNow() {
    return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }

  function scrollBottom() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  /** Convert basic markdown to HTML */
  function renderMarkdown(text) {
    return text
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.+?)\*/g, "<em>$1</em>")
      .replace(/^[•\-\*] (.+)$/gm, "<li>$1</li>")
      .replace(/(<li>.*<\/li>)/gs, "<ul>$1</ul>")
      .replace(/\n/g, "<br>");
  }

  function appendMsg(text, role, imageUrl) {
    // Text bubble
    const bubble = document.createElement("div");
    bubble.className = `cw-msg ${role}`;
    if (role === "bot") {
      bubble.innerHTML = renderMarkdown(text);
    } else {
      bubble.textContent = text;
    }
    messagesEl.insertBefore(bubble, typingEl);

    // Chart image as its own element below the bubble
    if (imageUrl) {
      const imgWrap = document.createElement("div");
      imgWrap.style.cssText = "align-self:flex-start;max-width:90%;margin-top:4px;";

      const img = document.createElement("img");
      img.src   = imageUrl;
      img.alt   = "Chart";
      img.style.cssText = "max-width:100%;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,0.12);display:block;";
      img.onerror = () => {
        imgWrap.innerHTML = "<span style='color:#ef4444;font-size:12px;'>⚠️ Chart could not be loaded</span>";
      };

      imgWrap.appendChild(img);
      messagesEl.insertBefore(imgWrap, typingEl);
    }

    // Timestamp
    const time = document.createElement("div");
    time.className   = `cw-time ${role === "user" ? "right" : "left"}`;
    time.textContent = timeNow();
    messagesEl.insertBefore(time, typingEl);

    scrollBottom();
  }

  function showTyping() { typingEl.classList.add("active");    scrollBottom(); }
  function hideTyping() { typingEl.classList.remove("active"); }

  async function sendMessage() {
    const text = inputEl.value.trim();
    if (!text) return;

    appendMsg(text, "user", null);
    inputEl.value = "";
    showTyping();

    try {
      const resp = await fetch(AGENT_URL, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ session_id: SESSION_ID, message: text }),
      });

      if (!resp.ok) throw new Error(`Server ${resp.status}`);

      const data = await resp.json();
      hideTyping();

      // Prefer base64 for image rendering, fall back to image_url
      const imageUrl = data.base64
        ? `data:image/png;base64,${data.base64}`
        : (data.image_url || null);

      appendMsg(data.response, "bot", imageUrl);

    } catch (err) {
      hideTyping();
      appendMsg("⚠️ Could not reach the AI agent. Make sure the server is running on port 5000.", "bot", null);
      console.error("Agent error:", err);
    }
  }

  document.getElementById("cwSendBtn").addEventListener("click", () => sendMessage());
  inputEl.addEventListener("keydown", e => { if (e.key === "Enter") sendMessage(); });

  // Close on X button
  document.getElementById("cwCloseBtn").addEventListener("click", () => {
    overlay.classList.remove("open");
  });

  // Close when clicking outside the chat window
  overlay.addEventListener("click", e => {
    if (e.target === overlay) overlay.classList.remove("open");
  });

  /* ── Public API ────────────────────────────────────────────────────── */
  window.openChat = function () {
    overlay.classList.add("open");
    inputEl.focus();
  };

})();
