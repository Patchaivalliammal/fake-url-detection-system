
const urlForm = document.getElementById("urlForm");
const urlInput = document.getElementById("urlInput");
const analyzeBtn = document.getElementById("analyzeBtn");

const loading = document.getElementById("loading");
const result = document.getElementById("result");
const errorBox = document.getElementById("error");

const resultIcon = document.getElementById("resultIcon");
const resultTitle = document.getElementById("resultTitle");
const resultMessage = document.getElementById("resultMessage");

const confidenceValue = document.getElementById("confidenceValue");
const confidenceBar = document.getElementById("confidenceBar");


function hideAllMessages() {
    loading.classList.add("hidden");
    result.classList.add("hidden");
    errorBox.classList.add("hidden");
}


function showError(message) {
    hideAllMessages();

    errorBox.textContent = message;
    errorBox.classList.remove("hidden");
}


function showResult(data) {
    hideAllMessages();

    result.classList.remove("safe", "danger");

    if (data.prediction === "Phishing") {
        result.classList.add("danger");
        resultIcon.textContent = "⚠️";
    } else {
        result.classList.add("safe");
        resultIcon.textContent = "🛡️";
    }

    resultTitle.textContent = data.prediction;
    resultMessage.textContent = data.message;

    confidenceValue.textContent =
        `${data.confidence}%`;

    confidenceBar.style.width =
        `${Math.min(100, Math.max(0, data.confidence))}%`;

    result.classList.remove("hidden");
}


urlForm.addEventListener("submit", async function(event) {

    event.preventDefault();

    const url = urlInput.value.trim();

    if (!url) {
        showError("Please enter a URL.");
        return;
    }

    hideAllMessages();

    loading.classList.remove("hidden");
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = "Analyzing...";

    try {

        const response = await fetch("/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                url: url
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error || "Unable to analyze URL."
            );
        }

        showResult(data);

    } catch (error) {

        showError(
            error.message ||
            "Something went wrong. Please try again."
        );

    } finally {

        loading.classList.add("hidden");
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = "🔍 Analyze URL";

    }

});
