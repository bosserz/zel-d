document.addEventListener("DOMContentLoaded", function () {
  const categoryFilter = document.getElementById("categoryFilter");
  const tagFilter = document.getElementById("tagFilter");
  const productCards = document.querySelectorAll(".product-card");

  function filterProducts() {
    const selectedCategory = categoryFilter ? categoryFilter.value : "all";
    const selectedTag = tagFilter ? tagFilter.value : "all";

    productCards.forEach(card => {
      const category = card.dataset.category;
      const tags = card.dataset.tags;

      let show = true;

      if (selectedCategory !== "all" && category !== selectedCategory) {
        show = false;
      }

      if (selectedTag !== "all" && !tags.includes(selectedTag)) {
        show = false;
      }

      card.style.display = show ? "block" : "none";
    });
  }

  if (categoryFilter) categoryFilter.addEventListener("change", filterProducts);
  if (tagFilter) tagFilter.addEventListener("change", filterProducts);
});