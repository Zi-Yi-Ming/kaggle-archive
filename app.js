// light interaction: highlight status cards on load
document.addEventListener("DOMContentLoaded", () => {
  const els = document.querySelectorAll(".status-grid .v");
  els.forEach((el, i) => {
    el.style.opacity = "0";
    el.style.transform = "translateY(4px)";
    el.style.transition = "opacity 0.35s ease, transform 0.35s ease";
    setTimeout(() => {
      el.style.opacity = "1";
      el.style.transform = "none";
    }, 80 * i);
  });
});
