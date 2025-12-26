// Dashboard.js
// Handles lecturer and student dashboard logic + Phase 2 session workflow

const API_BASE = "http://127.0.0.1:8000";

// ------------------------
// AUTH HELPERS
// ------------------------
function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("role");
  localStorage.removeItem("user_id");
  window.location.href = "login.html";
}

function getToken() {
  return localStorage.getItem("access_token");
}

function getHeaders() {
  return {
    "Content-Type": "application/json",
    Authorization: "Bearer " + getToken(),
  };
}

const role = localStorage.getItem("role");
const userId = localStorage.getItem("user_id");

// redirect if not logged in
if (!getToken() || !role || !userId) {
  window.location.href = "login.html";
}

// ------------------------
// ON PAGE LOAD
// ------------------------

document.addEventListener("DOMContentLoaded", function () {
  if (role === "lecturer") {
    loadLecturerDashboard();

    const generateBtn = document.getElementById("generateSessionBtn");
    if (generateBtn) {
      generateBtn.addEventListener("click", createSession);
    }
  } else if (role === "student") {
    loadStudentDashboard();
  } else {
    logout();
  }
});

// ================================
//      LECTURER DASHBOARD
// ================================
function loadLecturerDashboard() {
  document.getElementById("lecturerSection").style.display = "block";
  document.getElementById("dashboardSubtitle").innerText = "Lecturer Dashboard";

  // 1. Load lecturer profile
  fetch(`${API_BASE}/lecturers/me`, {
    headers: getHeaders(),
  })
    .then((res) => res.json())
    .then((data) => {
      document.getElementById("username").innerText = data.full_name;
    });

  // 2. Load attendance records
  loadLecturerAttendance();
}

// Load all lecturer attendance
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
        const row = `
                    <tr>
                        <td>${idx + 1}</td>
                        <td>${rec.student_id}</td>
                        <td>${rec.course || "N/A"}</td>
                        <td>${rec.date}</td>
                        <td>${rec.status}</td>
                    </tr>
                `;
        tbody.innerHTML += row;
      });
    });
}

// ---------------------------
// PHASE 2: Create Attendance Session
// ---------------------------
function createSession() {
  const submitBtn = document.getElementById("generateSessionBtn");
  if (submitBtn) submitBtn.disabled = true;

  console.log("Generate session clicked");
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
    .then((res) => {
      if (!res.ok) {
        return res.json().then((data) => {
          throw new Error(data.detail || "Session creation failed.");
        });
      }
      return res.json();
    })
    .then((session) => {
      const codeSpan = document.getElementById("generatedSessionCode");
      const codeBox = document.getElementById("sessionCodeBox");

      codeSpan.innerText = session.session_code;
      codeBox.classList.remove("d-none");
    })
    .catch((err) => alert(err.message))
    .finally(() => {
      if (submitBtn) submitBtn.disabled = false;
    });
}

// ================================
//        STUDENT DASHBOARD
// ================================
function loadStudentDashboard() {
  document.getElementById("studentSection").style.display = "block";
  document.getElementById("dashboardSubtitle").innerText = "Student Dashboard";

  // 1. Load student profile
  fetch(`${API_BASE}/students/me`, {
    headers: getHeaders(),
  })
    .then((res) => res.json())
    .then((data) => {
      document.getElementById("username").innerText = data.full_name;
    });

  // 2. Load attendance
  loadStudentAttendance();

  // 3. Code submit handler
  const codeForm = document.getElementById("codeForm");
  codeForm.addEventListener("submit", function (e) {
    e.preventDefault();
    verifySessionCode();
  });
}

// Load all student attendance
function loadStudentAttendance() {
  fetch(`${API_BASE}/students/me/attendance`, {
    headers: getHeaders(),
  })
    .then((res) => res.json())
    .then((attendance) => {
      const tbody = document
        .getElementById("studentAttendanceTable")
        .querySelector("tbody");

      tbody.innerHTML = "";

      attendance.forEach((rec, idx) => {
        const row = `
                    <tr>
                        <td>${idx + 1}</td>
                        <td>${rec.course || "N/A"}</td>
                        <td>${rec.lecturer_name || "N/A"}</td>
                        <td>${rec.date}</td>
                        <td>${rec.status}</td>
                    </tr>
                `;
        tbody.innerHTML += row;
      });
    });
}

// ---------------------------
// PHASE 2: Student verifies session code
// ---------------------------
function verifySessionCode() {
  const code = document.getElementById("sessionCodeInput").value.trim();

  fetch(`${API_BASE}/students/verify_session_code?session_code=${code}`, {
    method: "POST",
    headers: getHeaders(),
  })
    .then((res) => {
      if (!res.ok) {
        document.getElementById("invalidCodeBox").classList.remove("d-none");
        throw new Error("Invalid code");
      }
      return res.json();
    })
    .then((session) => {
      fetch(`${API_BASE}/attendance/session/${session.id}/status`, {
        headers: getHeaders(),
      })
        .then((res) => res.json())
        .then((status) => {
          displaySessionDetails(session, status.marked);
        });
    })
    .catch((err) => console.log(err));
}

function displaySessionDetails(session, alreadyMarked) {
  const containerId = `session-${session.id}`;
  // Prevent duplicate rendering
  if (document.getElementById(containerId)) return;

  const container = document.createElement("div");
  container.className = "card shadow mt-4";
  container.id = containerId;

  container.innerHTML = `
    <div class="card-body">
      <h4 class="fw-bold mb-3">Active Attendance Session</h4>

      <p><strong>Course Code:</strong> ${session.course_code}</p>
      <p><strong>Course Title:</strong> ${session.course_title}</p>
      <p><strong>Date:</strong> ${session.date}</p>

      ${
        alreadyMarked
          ? `<div class="alert alert-secondary mt-3">
               Attendance already marked for this session.
             </div>`
          : `<button
               class="btn btn-success mt-3"
               onclick="markAttendance(${session.lecturer_id}, ${session.id})"
               Mark Attendance
             </button>`
      }

      <div id="attendanceStatus-${session.id}" class="mt-3"></div>
    </div>
  `;

  document.getElementById("activeSessionContainer").prepend(container);
}

function markAttendance(lecturerId, sessionId) {
  const payload = {
    lecturer_id: lecturerId,
    session_id: sessionId,
    status: "present",
  };

  fetch(`${API_BASE}/attendance/mark`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(payload),
  })
    .then((res) => {
      if (!res.ok) {
        return res.json().then((data) => {
          throw new Error(data.detail || "Attendance failed");
        });
      }
      return res.json();
    })
    .then(() => {
      const statusBox = document.getElementById(
        `attendanceStatus-${sessionId}`
      );

      statusBox.innerHTML = `
        <div class="alert alert-success">
          Attendance marked successfully ✅
        </div>
      `;
    })
    .catch((err) => {
      document.getElementById(`attendanceStatus-${sessionId}`).innerHTML = `
        <div class="alert alert-danger">${err.message}</div>
      `;
    });
}
