/* Apply reading preferences before first paint to avoid a flash. */
(function () {
  try {
    var root = document.documentElement;
    var size = localStorage.getItem("src-text-size");
    var contrast = localStorage.getItem("src-contrast");
    var motion = localStorage.getItem("src-motion");
    if (size === "lg" || size === "xl") root.setAttribute("data-size", size);
    if (contrast === "high") root.setAttribute("data-contrast", "high");
    if (motion === "reduce") root.setAttribute("data-motion", "reduce");
  } catch (error) {
    /* localStorage can be unavailable in private contexts. */
  }
  document.documentElement.classList.add("js");
})();
