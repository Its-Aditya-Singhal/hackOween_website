/* ImpactEcho Dashboard — fully dynamic from backend */

const user = { 
  username: "Manaswi G",
  walletAddress: localStorage.getItem('walletAddress') || "" 
};
const livesPer25 = 25;

/* --- DOM References --- */
const usernameBanner = document.getElementById("username-banner");
const welcomeInline = document.getElementById("welcomeInline");
const usernameInput = document.getElementById("usernameInput");
const causesGrid = document.getElementById("causesGrid");
const totalImpactEl = document.getElementById("totalImpact");
const donationsMadeEl = document.getElementById("donationsMade");
const causesSupportedEl = document.getElementById("causesSupported");
const livesImpactedEl = document.getElementById("livesImpacted");
const impactProgressBar = document.getElementById("impactProgressBar");
const impactPercent = document.getElementById("impactPercent");
const recentList = document.getElementById("recentList");

/* --- State --- */
let causes = [];
let totalImpact = 0;
let donationsMade = 0;
let livesImpacted = 0;
const supportedCauses = new Set();
const recentDonations = [];

/* --- Helper Functions --- */
const formatINR = (num) => "₹" + Number(num).toLocaleString();

/* --- Username Logic --- */
function renderUsername() {
  usernameBanner.textContent = user.username;
  welcomeInline.textContent = user.username;
  usernameInput.value = user.username;
}
usernameInput.addEventListener("input", (e) => {
  user.username = e.target.value || "anonymous";
  renderUsername();
});

/* --- Fetch Causes from Backend --- */
async function fetchCauses() {
  try {
    const res = await fetch("/causes");
    const data = await res.json();
    causes = data;
    renderCauses();
    updateStats();
  } catch (err) {
    console.error("Error fetching causes:", err);
    causesGrid.innerHTML = "<p class='muted'>Unable to load causes at the moment.</p>";
  }
}

/* --- Render Causes with Smooth Animations --- */
function renderCauses() {
  causesGrid.innerHTML = "";
  causes.forEach((cause, index) => {
    const percent = Math.min((cause.raised / cause.goal) * 100, 100).toFixed(1);
    const card = document.createElement("div");
    card.className = "cause-card card";
    card.style.animationDelay = `${index * 0.1}s`;
    card.innerHTML = `
      <img src="${cause.image}" alt="${cause.title}" class="cause-img">
      <h3>${cause.title}</h3>
      <p>${cause.description}</p>
      <div class="progress-wrap-small">
        <div class="progress-small-fill" style="width:0%;"></div>
      </div>
      <p class="muted small">${formatINR(cause.raised)} raised of ${formatINR(cause.goal)}</p>
      <button class="fund-btn" data-id="${cause.id}">Fund Cause</button>
    `;
    causesGrid.appendChild(card);
    
    // Animate progress bar with delay
    setTimeout(() => {
      const progressBar = card.querySelector('.progress-small-fill');
      if (progressBar) {
        progressBar.style.width = `${percent}%`;
      }
    }, 100 + (index * 100));
  });

  document.querySelectorAll(".fund-btn").forEach((btn) => {
    btn.addEventListener("click", handleFundClick);
  });

  causesSupportedEl.textContent = supportedCauses.size;
}

/* --- Handle Funding with Enhanced Feedback --- */
async function handleFundClick(e) {
  const button = e.target;
  const id = Number(button.getAttribute("data-id"));
  const cause = causes.find((c) => c.id === id);
  const amount = Number(prompt(`Enter amount to fund "${cause.title}" (in ₹):`));

  if (!amount || isNaN(amount) || amount <= 0) return;

  // Disable button during processing
  button.disabled = true;
  const originalText = button.textContent;
  button.textContent = 'Processing...';

  // Simulate processing delay for better UX
  setTimeout(async () => {
    // Update locally
    cause.raised += amount;
    totalImpact += amount;
    donationsMade++;
    livesImpacted += Math.floor(amount / livesPer25);
    supportedCauses.add(cause.title);

    // Log donation to backend
    try {
      await fetch('/api/log-donation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          wallet_address: user.walletAddress,
          cause_title: cause.title,
          amount: amount
        })
      });
    } catch (err) {
      console.error('Error logging donation:', err);
    }

    // Update UI with animations
    renderCauses();
    updateStats();
    addRecentDonation(cause.title, amount);

    // Show success feedback
    showSuccessAnimation(button);
    
    // Re-enable button
    button.disabled = false;
  }, 500);
}

/* --- Stats Update with Smooth Animations --- */
function updateStats() {
  // Animate number changes
  animateNumber(totalImpactEl, totalImpact, formatINR);
  animateNumber(donationsMadeEl, donationsMade);
  animateNumber(livesImpactedEl, livesImpacted);
  causesSupportedEl.textContent = supportedCauses.size;

  const avgProgress =
    causes.reduce((sum, c) => sum + (c.raised / c.goal) * 100, 0) / causes.length || 0;
  const percent = Math.min(avgProgress, 100).toFixed(1);
  
  // Smooth progress bar animation
  setTimeout(() => {
    impactProgressBar.style.width = `${percent}%`;
    impactPercent.textContent = `${percent}%`;
  }, 100);
}

/* --- Animate Numbers --- */
function animateNumber(element, targetValue, formatter = null) {
  const currentValue = parseInt(element.textContent.replace(/[^0-9]/g, '')) || 0;
  const duration = 800;
  const steps = 30;
  const increment = (targetValue - currentValue) / steps;
  let current = currentValue;
  let step = 0;

  const timer = setInterval(() => {
    step++;
    current += increment;
    
    if (step >= steps) {
      current = targetValue;
      clearInterval(timer);
    }
    
    element.textContent = formatter ? formatter(Math.floor(current)) : Math.floor(current);
  }, duration / steps);
}

/* --- Recent Donations with Animation --- */
function addRecentDonation(title, amount) {
  // Remove "No donations yet" message if present
  const noDonatonsMsg = recentList.querySelector('.muted');
  if (noDonatonsMsg) {
    noDonatonsMsg.remove();
  }

  const li = document.createElement("li");
  li.textContent = `Funded ${formatINR(amount)} to "${title}"`;
  li.style.animation = 'none';
  recentList.prepend(li);
  
  // Trigger animation
  setTimeout(() => {
    li.style.animation = '';
  }, 10);

  if (recentList.children.length > 6) {
    const lastItem = recentList.lastChild;
    lastItem.style.transition = 'all 0.3s ease';
    lastItem.style.opacity = '0';
    lastItem.style.transform = 'translateX(-20px)';
    setTimeout(() => {
      recentList.removeChild(lastItem);
    }, 300);
  }
}

/* --- Add Success Animation to Donation --- */
function showSuccessAnimation(button) {
  const originalText = button.textContent;
  button.textContent = '✓ Funded!';
  button.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
  
  setTimeout(() => {
    button.textContent = originalText;
  }, 2000);
}

/* --- Logout Functionality --- */
const logoutBtn = document.getElementById("logoutBtn");
if (logoutBtn) {
  logoutBtn.addEventListener("click", () => {
    // Clear local storage and redirect to logout endpoint
    localStorage.clear();
    sessionStorage.clear();
    window.location.href = "/donator-logout";
  });
}

/* --- Initialize --- */
function init() {
  renderUsername();
  fetchCauses();
}

document.addEventListener("DOMContentLoaded", init);

