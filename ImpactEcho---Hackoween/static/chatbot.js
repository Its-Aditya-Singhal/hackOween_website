document.addEventListener("DOMContentLoaded", () => {
  // ---------- Mock Blockchain Data ----------
  const donationData = {
    donationCause: "Clean Water Initiative",
    verifiedByAI: true,
    badge: "Silver Supporter",
    amount: "2.5 ETH",
    paymentDetails: {
      txHash: "0xabc123def456...",
      status: "Confirmed",
      timestamp: "2025-10-14T08:26:00Z",
    },
  };

  // ---------- Inject Chatbot HTML ----------
  document.body.insertAdjacentHTML("beforeend", `
    <button id="chatbot-button">💬</button>
    <div id="chatbot">
      <div id="chatbot-header">ImpactEcho 🤖</div>
      <div id="chatbot-messages"></div>
      <div id="chatbot-input">
        <input id="user-input" type="text" placeholder="Ask something..." />
        <button id="send-btn">Send</button>
      </div>
    </div>
  `);

  // ---------- Elements ----------
  const chatBtn = document.getElementById("chatbot-button");
  const chatWindow = document.getElementById("chatbot");
  const messagesDiv = document.getElementById("chatbot-messages");
  const userInput = document.getElementById("user-input");
  const sendBtn = document.getElementById("send-btn");

  // ---------- Toggle Chat ----------
  chatBtn.onclick = () => {
    chatWindow.style.display = chatWindow.style.display === "flex" ? "none" : "flex";
  };

  // ---------- Send Message ----------
  sendBtn.onclick = handleUserMessage;
  userInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") handleUserMessage();
  });

  // ---------- Initial Greeting ----------
  addMessage("bot", "Hey! I'm ImpactEcho 🤖. Ask me about your donation or payment progress!");

  // ---------- Core Chat Logic ----------
  function handleUserMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    addMessage("user", text);
    userInput.value = "";

    showTypingAnimation();

    setTimeout(() => {
      removeTypingAnimation();
      const reply = generateAIResponse(text.toLowerCase());
      addMessage("bot", reply);
    }, 1000);
  }

  function addMessage(sender, text) {
    const msgDiv = document.createElement("div");
    msgDiv.classList.add("message", sender);
    msgDiv.textContent = text;
    messagesDiv.appendChild(msgDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  }

  // ---------- Typing Indicator ----------
  let typingDiv;
  function showTypingAnimation() {
    typingDiv = document.createElement("div");
    typingDiv.classList.add("typing");
    typingDiv.innerHTML = '<span class="dot"></span><span class="dot"></span><span class="dot"></span>';
    messagesDiv.appendChild(typingDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  }
  function removeTypingAnimation() {
    if (typingDiv) typingDiv.remove();
  }

  // ---------- Simple Keyword Responses ----------
  function generateAIResponse(text) {
    if (["hi", "hello", "hey", "yo", "hola"].some(w => text.includes(w)))
      return "Hey there 👋 I'm ImpactEcho — your friendly donation assistant! Ask me about your donation status, verification, or badge.";

    if (text.includes("amount") || text.includes("how much"))
      return `You donated ${donationData.amount} to the "${donationData.donationCause}" campaign 💧.`;

    if (text.includes("cause") || text.includes("campaign"))
      return `Your donation supports the "${donationData.donationCause}" initiative — a great choice! 🌍`;

    if (text.includes("verified"))
      return donationData.verifiedByAI
        ? "✅ Your donation has been verified by our AI system — it's authentic and recorded on-chain."
        : "⚠️ It seems your donation is still awaiting AI verification.";

    if (text.includes("badge"))
      return `You've earned the "${donationData.badge}" badge 🏅. Thanks for making an impact!`;

    if (text.includes("payment") || text.includes("status"))
      return `Transaction status: ${donationData.paymentDetails.status} (${donationData.paymentDetails.txHash.slice(0,10)}...).`;

    if (text.includes("thank") || text.includes("thanks"))
      return "You're most welcome 💙 Every bit of support matters.";

    const fallbacks = [
      "Hmm, could you rephrase that? I might’ve missed something.",
      "I'm here to help with your donation details — maybe ask about verification, badge, or status?",
      "Not sure I got that, but your donation is doing good things 🌱",
    ];
    return fallbacks[Math.floor(Math.random() * fallbacks.length)];
  }
});
