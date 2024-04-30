const nav = document.querySelector("#nav-menu");
const navBtn = document.querySelector("#nav-btn");
const navLines = navBtn.children;
navBtn.addEventListener("click", () => {
    nav.classList.toggle("nav-close");
    nav.classList.toggle("nav-open");
    navLines[1].style.visibility = navLines[1].style.visibility == "hidden" ? "visible" : "hidden";
    navLines[0].classList.toggle("rotate-line1");
    navLines[2].classList.toggle("rotate-line2");
});