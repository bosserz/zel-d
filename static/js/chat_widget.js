(function () {
  const CHAT_ENDPOINT = "/api/chat";

  function createWidget() {
    const container = document.createElement("div");
    container.className = "zeld-chat-container";

    container.innerHTML = `
      <button class="zeld-chat-toggle" aria-label="Open chat">
        💬
      </button>

      <div class="zeld-chat-window" aria-hidden="true">
        <div class="zeld-chat-header">
          <div>
            <strong>Zel-D Support</strong>
            <div class="zeld-chat-subtitle">Wellness assistance</div>
          </div>
          <button class="zeld-chat-close" aria-label="Close chat">×</button>
        </div>

        <div class="zeld-chat-messages" role="log" aria-live="polite"></div>

        <form class="zeld-chat-form">
          <input
            type="text"
            class="zeld-chat-input"
            placeholder="Ask about products, shipping..."
            required
          />
          <button type="submit" class="zeld-chat-send">Send</button>
        </form>
      </div>
    `;

    document.body.appendChild(container);
    initEvents(container);
  }

  function initEvents(container) {
    const toggleBtn = container.querySelector(".zeld-chat-toggle");
    const closeBtn = container.querySelector(".zeld-chat-close");
    const chatWindow = container.querySelector(".zeld-chat-window");
    const form = container.querySelector(".zeld-chat-form");
    const input = container.querySelector(".zeld-chat-input");
    const messages = container.querySelector(".zeld-chat-messages");

    function openChat() {
      chatWindow.classList.add("open");
      toggleBtn.style.visibility = "hidden";
      input.focus();
    }

    function closeChat() {
      chatWindow.classList.remove("open");
      toggleBtn.style.visibility = "visible";
    }

    toggleBtn.addEventListener("click", openChat);
    closeBtn.addEventListener("click", closeChat);

    form.addEventListener("submit", async function (e) {
      e.preventDefault();
      const userMessage = input.value.trim();
      if (!userMessage) return;

      addMessage("user", userMessage);
      input.value = "";
      input.disabled = true;

      addTyping();

      try {
        const response = await fetch(CHAT_ENDPOINT, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: userMessage })
        });

        const data = await response.json();
        removeTyping();

        addMessage("bot", data.reply || "Sorry, something went wrong.");
      } catch (err) {
        removeTyping();
        addMessage("bot", "Connection issue. Please try again later.");
      }

      input.disabled = false;
      input.focus();
    });

    function addMessage(role, text) {
      const msg = document.createElement("div");
      msg.className = `zeld-chat-message ${role}`;
      msg.textContent = text;
      messages.appendChild(msg);
      messages.scrollTop = messages.scrollHeight;
    }

    function addTyping() {
      const typing = document.createElement("div");
      typing.className = "zeld-chat-message bot typing";
      typing.id = "zeld-typing";
      typing.textContent = "Zel-D is typing...";
      messages.appendChild(typing);
      messages.scrollTop = messages.scrollHeight;
    }

    function removeTyping() {
      const el = document.getElementById("zeld-typing");
      if (el) el.remove();
    }
  }

  document.addEventListener("DOMContentLoaded", createWidget);
})();