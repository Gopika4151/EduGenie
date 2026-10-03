const form = document.getElementById("eduForm");
const task = document.getElementById("task");
const model = document.getElementById("model");
const level = document.getElementById("level");
const levelLabel = document.getElementById("levelLabel");
const inputText = document.getElementById("inputText");
const submitBtn = document.getElementById("submitBtn");
const resultCard = document.getElementById("resultCard");
const result = document.getElementById("result");
const errorBox = document.getElementById("error");
const copyBtn = document.getElementById("copyBtn");
const healthBadge = document.getElementById("healthBadge");


task.addEventListener("change", () => {
    const isLearn = task.value === "learn";
    level.classList.toggle("hidden", !isLearn);
    levelLabel.classList.toggle("hidden", !isLearn);

    const placeholders = {
        qa: "Example: Which is the largest ocean?",
        explain: "Example: Explain the Pythagoras theorem.",
        quiz: "Paste a passage or topic to generate 3 MCQs.",
        summarize: "Paste a long educational passage to summarize.",
        learn: "Example: SQL"
    };
    inputText.placeholder = placeholders[task.value];
});

async function checkHealth() {
    try {
        const response = await fetch("/health");
        const data = await response.json();
        healthBadge.textContent = data.status === "ok" ? "API online" : "API issue";
    } catch {
        healthBadge.textContent = "API offline";
    }
}

function showText(text) {
    result.innerHTML = `<div class="answer"></div>`;
    result.querySelector(".answer").textContent = text;
}

function showQuiz(items) {
    result.innerHTML = items.map((item, index) => `
        <div class="quiz-item">
            <strong>${index + 1}. ${escapeHtml(item.question)}</strong>
            <div>
                ${item.options.map((option) => `
                    <label class="quiz-option">
                        <input type="radio" name="q${index}" value="${escapeAttr(option)}">
                        ${escapeHtml(option)}
                    </label>
                `).join("")}
            </div>
            <button type="button" class="secondary check-answer" data-index="${index}">Check answer</button>
            <div class="quiz-feedback" id="feedback-${index}"></div>
        </div>
    `).join("");

    document.querySelectorAll(".check-answer").forEach(button => {
        button.addEventListener("click", () => {
            const index = Number(button.dataset.index);
            const selected = document.querySelector(`input[name="q${index}"]:checked`);
            const feedback = document.getElementById(`feedback-${index}`);
            const options = document.querySelectorAll(`input[name="q${index}"]`);
            options.forEach(input => {
                input.parentElement.classList.remove("correct", "wrong");
                if (input.value === items[index].correct_answer) {
                    input.parentElement.classList.add("correct");
                }
            });

            if (!selected) {
                feedback.textContent = "Choose an answer first.";
            } else if (selected.value === items[index].correct_answer) {
                feedback.textContent = "Correct!";
            } else {
                feedback.textContent = `Not quite. Correct answer: ${items[index].correct_answer}`;
                selected.parentElement.classList.add("wrong");
            }
        });
    });
}

function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, char => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
    }[char]));
}

function escapeAttr(value) {
    return String(value).replace(/"/g, "&quot;");
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const text = inputText.value.trim();
    if (!text) return;

    errorBox.classList.add("hidden");
    resultCard.classList.remove("hidden");
    submitBtn.disabled = true;
    submitBtn.textContent = "Working…";
    result.innerHTML = "";

    const endpointMap = {
        qa: "/qa",
        explain: "/explain",
        quiz: "/quiz",
        summarize: "/summarize",
        learn: "/learn/recommendations"
    };

    const selectedModel = model && model.value ? model.value : undefined;
    let body;
    if (task.value === "qa") {
        body = { question: text, model: selectedModel };
    } else if (task.value === "learn") {
        body = { topic: text, level: level.value, model: selectedModel };
    } else {
        body = { text, model: selectedModel };
    }


    try {
        const response = await fetch(endpointMap[task.value], {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body)
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || "The server returned an error.");
        }

        if (task.value === "qa") showText(data.answer);
        else if (task.value === "explain") showText(data.explanation);
        else if (task.value === "summarize") showText(data.summary);
        else if (task.value === "learn") showText(data.recommendations);
        else showQuiz(data.quiz);
    } catch (error) {
        errorBox.textContent = error.message;
        errorBox.classList.remove("hidden");
        resultCard.classList.add("hidden");
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "Run EduGenie";
    }
});

copyBtn.addEventListener("click", async () => {
    const text = result.innerText.trim();
    if (!text) return;
    await navigator.clipboard.writeText(text);
    copyBtn.textContent = "Copied!";
    setTimeout(() => copyBtn.textContent = "Copy", 1200);
});

checkHealth();
