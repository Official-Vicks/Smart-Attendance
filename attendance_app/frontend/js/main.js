/* =========================================================
   main.js — Core Frontend Interactions for Smart Attendance
   Improved version: consolidated role handling, safer fetch,
   redirect configuration, UX improvements (disable button).
   Author: Victory Chidiebere (updated)
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {
  console.log("Smart Attendance frontend loaded successfully ✅");

  // CONFIG: update LOGIN_PATH if your login page lives somewhere else
  // Examples:
  // - Relative (same folder): "login.html"
  // - Absolute frontend URL: "http://127.0.0.1:5500/frontend/login.html"
  const LOGIN_PATH = "login.html";

  // BACKEND API base - if deploying, consider setting via server/template/env
  const BASE_URL =
    location.hostname === "localhost"
      ? "http://127.0.0.1:8000"
      : "https://smart-attendance-api-q5ul.onrender.com";

  const signupForm = document.getElementById("registerForm");
  const roleSelect = document.getElementById("role");

  // Field wrappers & inputs
  const regField = document.getElementById("regNumberField");
  const deptField = document.getElementById("departmentField");
  const courseField = document.getElementById("courseField");
  const phoneField = document.getElementById("phonenumber");

  const fullNameInput = document.getElementById("fullname");
  const emailInput = document.getElementById("email");
  const passwordInput = document.getElementById("password");
  const regInput = document.getElementById("registrationNumber");
  const deptSelect = document.getElementById("department");
  const courseInput = document.getElementById("course");
  const phoneInput = document.getElementById("number"); // consider renaming to phoneNumber
  const submitBtn = signupForm.querySelector('[type="submit"]');

  // helper: show/hide wrapper element
  function show(el) {
    if (el) el.style.display = "block";
  }
  function hide(el) {
    if (el) el.style.display = "none";
  }

  // Consolidated role change handler
  function updateRoleUI() {
    const role = roleSelect.value;
    if (role === "student") {
      show(regField);
      show(deptField);
      hide(courseField);
      hide(phoneField);
      courseInput.value = "";
      phoneInput.value = "";
    } else if (role === "lecturer") {
      hide(regField);
      hide(deptField);
      show(courseField);
      show(phoneField);
      regInput.value = "";
      deptSelect.value = "";
    } else {
      // default: hide optional fields
      hide(regField);
      hide(deptField);
      hide(courseField);
      hide(phoneField);
      regInput.value = "";
      deptSelect.value = "";
      courseInput.value = "";
      phoneInput.value = "";
    }
  }

  // initial UI state
  updateRoleUI();
  roleSelect.addEventListener("change", updateRoleUI);

  // Simple alert utility
  function showAlert(message, type = "info", timeout = 3500) {
    const existing = document.querySelector(".custom-alert");
    if (existing) existing.remove();

    const alertDiv = document.createElement("div");
    alertDiv.className = `alert alert-${type} custom-alert position-fixed top-0 start-50 translate-middle-x mt-3 shadow`;
    alertDiv.setAttribute("role", "alert");
    alertDiv.style.zIndex = "9999";
    alertDiv.style.maxWidth = "420px";
    alertDiv.innerHTML = `<div class="text-center">${message}</div>`;

    document.body.appendChild(alertDiv);

    if (timeout > 0) setTimeout(() => alertDiv.remove(), timeout);
  }

  // fetch with timeout using AbortController
  async function fetchWithTimeout(resource, options = {}, ms = 10000) {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), ms);
    options.signal = controller.signal;
    try {
      const res = await fetch(resource, options);
      clearTimeout(id);
      return res;
    } catch (err) {
      clearTimeout(id);
      throw err;
    }
  }

  // Graceful JSON parse (fallback if non-JSON body)
  async function safeJson(res) {
    try {
      return await res.json();
    } catch (err) {
      return {
        detail:
          (await res.text().catch(() => "")) || res.statusText || "No details",
      };
    }
  }

  // Disable/enable submit button (with small UX text)
  function setSubmitting(isSubmitting) {
    if (!submitBtn) return;
    submitBtn.disabled = !!isSubmitting;
    if (isSubmitting) {
      submitBtn.dataset.origText = submitBtn.innerHTML;
      submitBtn.innerHTML = "Submitting...";
    } else {
      if (submitBtn.dataset.origText)
        submitBtn.innerHTML = submitBtn.dataset.origText;
    }
  }

  // FORM SUBMIT
  signupForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const fullName = fullNameInput.value.trim();
    const email = emailInput.value.trim();
    const password = passwordInput.value; // keep raw for server-side validation
    const role = roleSelect.value;

    const registration_number = regInput.value.trim();
    const department = deptSelect.value;
    const course = courseInput.value.trim();
    const phone = phoneInput.value.trim();

    if (!fullName || !email || !password || !role) {
      return showAlert("Please complete all required fields.", "warning");
    }

    let url = "";
    let payload = {};

    if (role === "student") {
      if (!registration_number || !department) {
        return showAlert(
          "Please provide registration number and department for students.",
          "warning"
        );
      }
      url = `${BASE_URL}/auth/register/student`;
      payload = {
        full_name: fullName,
        email,
        password,
        registration_number,
        department,
      };
    } else if (role === "lecturer") {
      if (!course) {
        return showAlert("Please provide course for lecturers.", "warning");
      }
      url = `${BASE_URL}/auth/register/lecturer`;
      payload = { full_name: fullName, email, password, course, phone };
    } else {
      return showAlert("Please select a valid role.", "warning");
    }

    setSubmitting(true);

    try {
      const res = await fetchWithTimeout(
        url,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        },
        12000
      ); // 12s timeout

      const data = await safeJson(res);

      if (!res.ok) {
        const msg =
          data.detail ||
          data.message ||
          `Registration failed (status ${res.status})`;
        showAlert(msg, "danger");
        setSubmitting(false);
        return;
      }

      showAlert(
        "Registration successful! Redirecting to login...",
        "success",
        3000
      );

      // choose redirect strategy:
      // 1) If LOGIN_PATH is absolute (starts with http), use it directly
      // 2) Otherwise resolve relative to current location
      setTimeout(() => {
        try {
          const isAbsolute = /^https?:\/\//i.test(LOGIN_PATH);
          if (isAbsolute) {
            window.location.href = LOGIN_PATH;
          } else {
            // resolves relative to current page
            window.location.href = new URL(
              LOGIN_PATH,
              window.location.href
            ).href;
          }
        } catch (err) {
          // fallback: try plain filename (best-effort)
          window.location.href = LOGIN_PATH;
        }
      }, 1200);
    } catch (err) {
      // handle AbortError vs network
      if (err.name === "AbortError") {
        showAlert("Request timed out. Please try again.", "danger");
      } else {
        showAlert(
          "Network error: " + (err.message || "Unknown error"),
          "danger"
        );
      }
      setSubmitting(false);
    }
  });
});
