const TIME_OUT = 500;
const feedbackForm = document.querySelector("#feedback-form");
function toggleFeedbackForm() {
    console.log("called");
    feedbackForm.style.display = feedbackForm.style.display == "none" ? "block" : "none";
    console.log("done");
}
const notLoginText = document.querySelector("#not-login-text");
function showNotLoginText() {
    notLoginText.style.display = "block";
}

const afterBuying = document.querySelector("#after-buying");
function showAfterBuying() {
    window.setTimeout(() => {
        feedbackForm.style.display = "block";
        const input_status = document.createElement("input");
        input_status.setAttribute("type", "hidden");
        input_status.setAttribute("name", "status");
        input_status.setAttribute("value", "bought");
        feedbackForm.appendChild(input_status);
        afterBuying.style.display = "block";
    }, TIME_OUT);
}