const API_BASE =
  location.hostname === "localhost"
    ? "http://127.0.0.1:8000"
    : "https://smart-attendance-api-q5ul.onrender.com";

const token = localStorage.getItem("access_token");
const role = localStorage.getItem("role");

if (!token || role !== "admin") {
  window.location.href = "login.html";
}

function getHeaders() {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

// =====================
// LOAD STUDENTS
// =====================
async function loadStudents() {
  const res = await fetch(`${API_BASE}/admin/students`, {
    headers: getHeaders(),
  });

  const data = await res.json();
  renderTable(data, "student");
}

// =====================
// LOAD LECTURERS
// =====================
async function loadLecturers() {
  const res = await fetch(`${API_BASE}/admin/lecturers`, {
    headers: getHeaders(),
  });

  const data = await res.json();
  renderTable(data, "lecturer");
}

// =====================
// RENDER TABLE
// =====================
function renderTable(data, role) {
  const container = document.getElementById("tableContainer");

  if (!data.length) {
    container.innerHTML = "<p>No records found.</p>";
    return;
  }

  let rows = data
    .map(
      (u) => `      <tr>         <td>${u.full_name}</td>         <td>${
        u.email
      }</td>         <td>${
        u.is_active ? "Active" : "Deactivated"
      }</td>         <td>
          ${
            u.is_active
              ? `<button class="btn btn-sm btn-danger" onclick="deactivate('${role}', ${u.id})">Deactivate</button>`
              : `<button class="btn btn-sm btn-success" onclick="reactivate('${role}', ${u.id})">Reactivate</button>`
          }         </td>       </tr>
    `
    )
    .join("");

  container.innerHTML = `     <table class="table table-bordered table-hover">       <thead class="table-light">         <tr>           <th>Name</th>           <th>Email</th>           <th>Status</th>           <th>Action</th>         </tr>       </thead>       <tbody>${rows}</tbody>     </table>
  `;
}

// =====================
// DEACTIVATE / REACTIVATE
// =====================
async function deactivate(role, id) {
  if (!confirm("Deactivate this account?")) return;

  await fetch(`${API_BASE}/admin/deactivate/${role}/${id}`, {
    method: "PATCH",
    headers: getHeaders(),
  });

  role === "student" ? loadStudents() : loadLecturers();
}

async function reactivate(role, id) {
  await fetch(`${API_BASE}/admin/reactivate/${role}/${id}`, {
    method: "PATCH",
    headers: getHeaders(),
  });

  role === "student" ? loadStudents() : loadLecturers();
}

// =====================
// LOGOUT
// =====================
function logout() {
  localStorage.clear();
  window.location.href = "login.html";
}

// Load students by default
loadStudents();
