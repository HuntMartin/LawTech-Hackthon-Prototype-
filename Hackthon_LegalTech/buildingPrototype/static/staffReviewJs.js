const chatDisplay = document.getElementById('chat-display');
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');

chatForm.addEventListener('submit', async (e) => {
  e.preventDefault();

  const userMessage = chatInput.value.trim();
  if (!userMessage) return;

  // Add user's message to chat display
  appendMessage('You', userMessage);

  // Clear input
  chatInput.value = '';

  try {
    const response = await fetch('/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: userMessage })
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    const aiResponse = data.answer || "Sorry, no response.";

    appendMessage('AI Consultant', aiResponse);

  } catch (error) {
    appendMessage('AI Consultant', `Error: ${error.message}`);
  }
});

function appendMessage(sender, message) {
  const p = document.createElement('p');
  p.innerHTML = `<strong>${sender}:</strong> ${message}`;
  chatDisplay.appendChild(p);

  // Scroll to bottom
  chatDisplay.scrollTop = chatDisplay.scrollHeight;
}

async function fetchAISummary() {
  const summaryDiv = document.getElementById('ai-summary-content');
  summaryDiv.innerHTML = '<p>Loading summary...</p>';

  try {
    const response = await fetch('/AImodel', { method: 'POST' });
    if (!response.ok) throw new Error('Network response was not ok');

    const data = await response.json();
    summaryDiv.innerHTML = `<p>${data.answer}</p>`;
  } catch (error) {
    summaryDiv.innerHTML = `<p>Error fetching summary: ${error.message}</p>`;
  }
}

// Call it once page loads
window.addEventListener('DOMContentLoaded', fetchAISummary);

// applicants.js

document.addEventListener("DOMContentLoaded", async () => {
  const select = document.getElementById("applicant-name-select");
  const search = document.getElementById("applicant-name-search");
  const ageEl = document.getElementById("applicant-age");
  const incomeEl = document.getElementById("applicant-income");
  const livingEl = document.getElementById("applicant-living");
  const problemEl = document.getElementById("applicant-problem");

  let applicants = [];

  // Fetch applicants from API
  async function loadApplicants() {
    try {
      const response = await fetch("/applicants");
      if (!response.ok) throw new Error("Failed to load applicants");
      applicants = await response.json();

      // Fill dropdown
      updateDropdown(applicants);

      // Display the first applicant by default
      if (applicants.length > 0) {
        displayApplicant(applicants[0]);
      }
    } catch (error) {
      console.error("Error loading applicants:", error);
    }
  }

  // Update dropdown options
  function updateDropdown(list) {
    select.innerHTML = "";
    list.forEach(applicant => {
      const option = document.createElement("option");
      option.value = applicant.id;
      option.textContent = applicant.Name;
      select.appendChild(option);
    });
  }

  // Display applicant details
  function displayApplicant(applicant) {
    ageEl.textContent = applicant.Age;
    incomeEl.textContent = applicant.Monthly_Income;
    livingEl.textContent = applicant.LivingCondition;
    problemEl.textContent = applicant.Problem;
  }

  // When dropdown changes
  select.addEventListener("change", () => {
    const selectedId = parseInt(select.value, 10);
    const applicant = applicants.find(a => a.id === selectedId);
    if (applicant) displayApplicant(applicant);
  });

  // Search filter
  search.addEventListener("input", () => {
    const term = search.value.toLowerCase();
    const filtered = applicants.filter(a =>
      a.Name.toLowerCase().includes(term)
    );
    updateDropdown(filtered);

    // Auto-display first match
    if (filtered.length > 0) {
      displayApplicant(filtered[0]);
    } else {
      ageEl.textContent = "";
      incomeEl.textContent = "";
      livingEl.textContent = "";
      problemEl.textContent = "";
    }
  });

  // Load data on page start
  loadApplicants();
});
