window.addEventListener("scroll", () => {
  const navbar = document.querySelector(".quiz-navbar");
  const scrollY = window.scrollY;

  // Adjust '300' to control how fast it fades out
  // (Higher number = slower fade, Lower number = faster fade)
  const fadePoint = 300;

  // Calculate opacity: goes from 1 (top) down to 0 (fully faded)
  let opacity = 1 - scrollY / fadePoint;

  // Ensure opacity stays strictly between 0 and 1
  opacity = Math.max(0, Math.min(1, opacity));

  // Apply opacity to the navbar
  navbar.style.opacity = opacity;

  // Optional: Disable pointer events when fully faded so users don't accidentally click invisible buttons
  navbar.style.pointerEvents = opacity === 0 ? "none" : "auto";
});


