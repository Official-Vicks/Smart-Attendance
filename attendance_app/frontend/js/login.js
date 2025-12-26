// login.js
// Handles user login (Lecturer & Student) for Smart Attendance System

document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("loginForm");

  // Attach event listener for login form submission
  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault(); // prevent form from refreshing the page

    // Extract values
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();
    const role = document.getElementById("role").value;

    // Basic validation
    if (!email || !password || !role) {
      alert("Please fill in all fields before submitting.");
      return;
    }

    try {
      // Send login request to FastAPI backend
      // determine endpoint based on selected role
      let url = "";
      if (role === "lecturer") {
        url = "http://127.0.0.1:8000/auth/login/lecturer";
        payload = {
          email,
          password,
        };
      } else if (role === "student") {
        url = "http://127.0.0.1:8000/auth/login/student";
        payload = {
          email,
          password,
        };
      } else {
        alert("Please select a role");
        return;
      }

      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const result = await response.json();

      if (response.ok) {
        // Save token in localStorage
        localStorage.setItem("access_token", result.access_token);
        localStorage.setItem("role", result.role);
        localStorage.setItem("user_id", result.user_id);
        // Redirect
        window.location.href = "dashboard.html";
      } else {
        alert(result.detail || "Invalid login credentials.");
      }
    } catch (error) {
      console.error("Error during login:", error);
      alert("An error occurred while logging in. Please try again.");
    }
  });
});
