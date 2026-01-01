// ===============================
// Dashboard.js (REBUILT BASELINE)
// ===============================
// Handles lecturer and student dashboard logic + Phase 2 session workflow

currentSessionId = null;
const API_BASE = "http://127.0.0.1:8000";

// -------------------------------
// Auth helpers
// -------------------------------
function getToken() {
  return localStorage.getItem("access_token");
}

function getHeaders() {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${getToken()}`,
  };
}

function logout() {
  localStorage.clear();
  window.location.href = "index.html";
}

const role = localStorage.getItem("role");
const userId = localStorage.getItem("user_id");

if (!getToken() || !role || !userId) {
  logout();
}

// -------------------------------
// Init
// -------------------------------
document.addEventListener("DOMContentLoaded", () => {
  if (role === "lecturer") {
    loadLecturerDashboard();
    bindSessionForm();
  } else if (role === "student") {
    loadStudentDashboard();
    bindSessionForm();
  } else {
    logout();
  }
});

// ===============================
// LECTURER DASHBOARD
// ===============================
function loadLecturerDashboard() {
  document.getElementById("lecturerSection").style.display = "block";
  document.getElementById("dashboardSubtitle").innerText = "Lecturer Dashboard";

  fetch(`${API_BASE}/lecturers/me`, {
    headers: getHeaders(),
  })
    .then((res) => res.json())
    .then((data) => {
      document.getElementById("username").innerText = data.full_name;
    });

  loadLecturerAttendance();
  loadLecturerSessions();
}

// Load Lecturer sessions
function loadLecturerSessions() {
  fetch(`${API_BASE}/lecturers/me/sessions`, {
    headers: getHeaders(),
  })
    .then((res) => res.json())
    .then((sessions) => {
      const box = document.getElementById("sessionCodeBox");
      const span = document.getElementById("generatedSessionCode");

      if (sessions.length > 0) {
        box.innerHTML = "";
        box.classList.remove("d-none");
        sessions
          .filter((session) => session.is_active)
          .forEach((session) => renderSession(session));
      }
    });
}

// Load lecturer attendance
function loadLecturerAttendance() {
  fetch(`${API_BASE}/lecturers/me/attendance`, {
    headers: getHeaders(),
  })
    .then((res) => res.json())
    .then((attendance) => {
      const tbody = document
        .getElementById("lecturerAttendanceTable")
        .querySelector("tbody");

      tbody.innerHTML = "";

      attendance.forEach((rec, idx) => {
        tbody.innerHTML += `
          <tr>
            <td>${idx + 1}</td>
            <td>${rec.student_id}</td>
            <td>${rec.student_name}</td>
            <td>${rec.course_code || "N/A"}</td>
            <td>${rec.date}</td>
            <td>${rec.status}</td>
          </tr>
        `;
      });
    });
}

// Bind session form ONCE
function bindSessionForm() {
  const sessionForm = document.getElementById("sessionForm");
  if (!sessionForm) return;

  sessionForm.onsubmit = function (e) {
    e.preventDefault();
    createSession();
  };

  const codeForm = document.getElementById("codeForm");
  if (!codeForm) return;
  codeForm.onsubmit = function (e) {
    e.preventDefault();
    verifySessionCode();
  };
}

// Create attendance session
function createSession() {
  const submitBtn = document.querySelector(
    "#sessionForm button[type='submit']"
  );
  if (submitBtn) submitBtn.disabled = true;

  const payload = {
    course_code: document.getElementById("courseCode").value,
    course_title: document.getElementById("courseTitle").value,
    date: document.getElementById("sessionDate").value,
  };

  fetch(`${API_BASE}/lecturers/create_session`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(payload),
  })
    .then(async (res) => {
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "Session creation failed");
      }

      const contentType = res.headers.get("content-type");
      if (contentType && contentType.includes("application/json")) {
        return res.json();
      }

      return null;
    })

    .then(() => {
      loadLecturerSessions();
    })
    .catch((err) => alert(err.message))
    .finally(() => {
      if (submitBtn) submitBtn.disabled = false;
    });
}

function closeSession(sessionId) {
  if (
    !confirm(
      "Closing this session will stop students from marking attendance. Continue?"
    )
  ) {
    return;
  }

  fetch(`${API_BASE}/lecturers/sessions/${sessionId}/close`, {
    method: "POST",
    headers: getHeaders(),
  })
    .then(async (res) => {
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "Failed to close session");
      }

      const contentType = res.headers.get("content-type");
      if (contentType && contentType.includes("application/json")) {
        return res.json();
      }

      return null;
    })
    .then(() => {
      alert("Session closed successfully");
      loadLecturerSessions();
    })
    .catch((err) => alert(err.message));
}

// ===============================
// STUDENT DASHBOARD
// ===============================
function loadStudentDashboard() {
  document.getElementById("studentSection").style.display = "block";
  document.getElementById("dashboardSubtitle").innerText = "Student Dashboard";

  fetch(`${API_BASE}/students/me`, {
    headers: getHeaders(),
  })
    .then((res) => res.json())
    .then((data) => {
      document.getElementById("username").innerText = data.full_name;
    });
}

// Verify session code
function verifySessionCode() {
  const submitBtn = document.querySelector("#codeForm button[type='submit']");
  if (submitBtn) submitBtn.disabled = true;

  const code = document.getElementById("sessionCodeInput").value.trim();
  if (!code) return;

  fetch(`${API_BASE}/students/verify_session_code?session_code=${code}`, {
    method: "POST",
    headers: getHeaders(),
  })
    .then((res) => {
      if (!res.ok) {
        document.getElementById("invalidCodeBox").classList.remove("d-none");
        throw new Error("Invalid session code");
      }
      return res.json();
    })
    .then((session) => {
      // 🔒 HIDE expired / closed sessions
      if (!session.is_active) {
        document.getElementById("invalidCodeBox").innerText =
          "This session is closed or expired";
        return; // ❗ stop execution here
      }
      displaySessionDetails(session);
    })
    .catch(() => {})
    .finally(() => {
      if (submitBtn) submitBtn.disabled = false;
    });
}

// Display session details
function displaySessionDetails(session) {
  const container = document.getElementById("sessionDetailsContainer");
  container.innerHTML = "";

  const card = document.createElement("div");
  card.className = "card p-3 mb-3";
  card.id = `session-${session.id}`;

  card.innerHTML = `
    <h5>${session.course_title}</h5>
    <p><strong>Course Code:</strong> ${session.course_code}</p>
    <p><strong>Date:</strong> ${session.date}</p>
    <button class="btn btn-success">Mark Attendance</button>
  `;

  const btn = card.querySelector("button");
  btn.onclick = () =>
    markAttendance(
      session.id,
      btn,
      card,
      session.course_code,
      session.course_title,
      session.date
    );

  container.appendChild(card);
}

// Mark attendance
function markAttendance(sessionId, btn, card, course_code, course_title, date) {
  btn.disabled = true;

  fetch(`${API_BASE}/attendance/mark`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({
      session_id: sessionId,
      status: "present",
      course_title: course_title,
      course_code: course_code,
      date: date,
    }),
  })
    .then(async (res) => {
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "Attendance failed");
      }

      // ✅ Chrome-safe: only parse JSON if it exists
      const contentType = res.headers.get("content-type");
      if (contentType && contentType.includes("application/json")) {
        return res.json();
      }

      return res;
    })

    .then(() => {
      btn.innerText = "Attendance Marked";
      //setTimeout(() => card.remove(), 5000);
    })
    .catch((err) => {
      alert(err.message);
      btn.disabled = false;
    });
}

//  ==============================================
// Session renderer
// ===============================================
function renderSession(session) {
  const container = document.getElementById("sessionCodeBox");
  container.classList.remove("d-none");

  const item = document.createElement("div");
  item.className = "alert alert-success mb-2";

  item.innerHTML = `
    <strong>${session.course_code}</strong> - ${session.course_title}<br>
    Session Code: <b id="code-${session.id}">${session.session_code}</b>
    <span class="float-end">${session.date}</span>

    <button
      class="btn btn-outline-secondary btn-sm ms-2"
      onclick="copySessionCode('${session.session_code}')"
    >
      Copy
    </button>

    ${
      session.is_active
        ? `
  <button
    class="btn btn-danger btn-sm mt-2"
    onclick="closeSession(${session.id})"
  >
    Close Session
  </button>
`
        : `<span class="badge bg-secondary mt-2">Closed</span>`
    }

  `;

  container.appendChild(item);
}

function copySessionCode(code) {
  if (!code) {
    alert("No session code to copy");
    return;
  }

  if (!navigator.clipboard) {
    alert("Clipboard access not supported in this browser.");
    return;
  }

  navigator.clipboard
    .writeText(code)
    .then(() => {
      alert("Session code copied to clipboard");
    })
    .catch(() => {
      alert("Failed to copy session code");
    });
}
