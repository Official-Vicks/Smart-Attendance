// ==============================
// Config & Auth
// ==============================
const token = localStorage.getItem("access_token");
const role = localStorage.getItem("role");
const BASE_URL =
  location.hostname === "localhost"
    ? "http://127.0.0.1:8000"
    : "https://smart-attendance-api-q5ul.onrender.com";
if (!token || !role) {
  window.location.href = "login.html";
}

function getHeaders() {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

// Base prefix based on role
const BASE_PATH = role === "lecturer" ? "/lecturers" : "/students";

// ==============================
// Load profile on page load
// ==============================
document.addEventListener("DOMContentLoaded", () => {
  loadProfile();
});

// ==============================
// Load Profile
// ==============================
async function loadProfile() {
  const res = await fetch(`${BASE_URL}${BASE_PATH}/me`, {
    headers: getHeaders(),
  });

  if (!res.ok) {
    alert("Failed to load profile");
    return;
  }

  const data = await res.json();

  document.getElementById("fullName").value = data.full_name;
  document.getElementById("email").value = data.email;
  document.getElementById("school").value = data.school;

  if (role === "student") {
    document.querySelector(".student-only").classList.remove("d-none");
    document.getElementById("department").value = data.department || "";
    document.getElementById("regNumber").value = data.registration_number || "";
  }

  if (role === "lecturer") {
    document.querySelector(".lecturer-only").classList.remove("d-none");
    document.getElementById("course").value = data.course || "";
  }
  if (data.profile_image) {
    // console.log("Profile image path from API:", data.profile_image);
    document.getElementById("profileImage").src = `${data.profile_image}`;
  }
}

// ==============================
// Update Profile
// ==============================
document.getElementById("profileForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const payload = {
    full_name: document.getElementById("fullName").value,
    email: document.getElementById("email").value,
  };

  if (role === "student") {
    payload.department = document.getElementById("department").value;
  }

  if (role === "lecturer") {
    payload.course = document.getElementById("course").value;
  }

  const res = await fetch(`${BASE_URL}${BASE_PATH}/update`, {
    method: "PUT",
    headers: getHeaders(),
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const err = await res.json();
    alert(err.detail || "Profile update failed");
    return;
  }

  alert("Profile updated successfully");
});

// ==============================
// Upload Profile Image
// ==============================
document.getElementById("imageInput").addEventListener("change", async (e) => {
  const file = e.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${BASE_URL}${BASE_PATH}/profile/image`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });

  if (!res.ok) {
    alert("Image upload failed");
    return;
  }

  const data = await res.json();
  const profileImage = document.getElementById("profileImage");
  profileImage.src = data.profile_image;
});

// ==============================
// Change Password
// ==============================
document
  .getElementById("passwordForm")
  .addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
      current_password: document.getElementById("oldPassword").value,
      new_password: document.getElementById("newPassword").value,
    };

    const res = await fetch(`${BASE_URL}${BASE_PATH}/change-password`, {
      method: "PUT",
      headers: getHeaders(),
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json();
      alert(err.detail || "Password change failed");
      return;
    }

    alert("Password updated successfully");
    e.target.reset();
  });

// ==============================
// Deactivate Account (Optional UI)
// ==============================
async function deactivateAccount() {
  if (!confirm("Are you sure you want to deactivate your account?")) return;

  const res = await fetch(`${BASE_URL}${BASE_PATH}/deactivate`, {
    method: "DELETE",
    headers: getHeaders(),
  });

  if (!res.ok) {
    alert("Failed to deactivate account");
    return;
  }

  alert("Account deactivated");
  logout();
}

// ==============================
// Logout
// ==============================
function logout() {
  localStorage.clear();
  window.location.href = "login.html";
}
