(() => {
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.getElementById("primary-nav");

  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      const isOpen = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(isOpen));
    });

    nav.querySelectorAll("a").forEach((a) => {
      a.addEventListener("click", () => {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  const yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  const corporateForm = document.getElementById("corporate-inquiry-form");
  if (corporateForm) {
    corporateForm.addEventListener("submit", (event) => {
      event.preventDefault();

      if (
        typeof corporateForm.checkValidity === "function" &&
        !corporateForm.checkValidity()
      ) {
        if (typeof corporateForm.reportValidity === "function") {
          corporateForm.reportValidity();
        }
        return;
      }

      const data = new FormData(corporateForm);
      const value = (name) => (data.get(name) || "Not provided").toString().trim() || "Not provided";
      const lines = [
        "Corporate inquiry for The Pecan House",
        "",
        `Company: ${value("company")}`,
        `Contact name: ${value("contact")}`,
        `Email: ${value("email")}`,
        `Phone: ${value("phone")}`,
        `Dates needed: ${value("dates")}`,
        `Number of guests: ${value("guests")}`,
        `Booking type: ${value("bookingType")}`,
        "",
        "Additional details:",
        value("notes"),
      ];

      const subject = encodeURIComponent("Corporate Inquiry - The Pecan House");
      const body = encodeURIComponent(lines.join("\n"));
      window.location.href = `mailto:stay@pecanhousetexarkana.info?subject=${subject}&body=${body}`;
    });
  }
})();
