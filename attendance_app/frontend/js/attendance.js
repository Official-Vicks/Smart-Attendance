document.addEventListener("DOMContentLoaded", () => {
  console.log("Attendance JS loaded ✅");

  const API_BASE =
    location.hostname === "localhost"
      ? "http://127.0.0.1:8000"
      : "https://smart-attendance-api-q5ul.onrender.com";

  const token = localStorage.getItem("access_token");
  const role = localStorage.getItem("role");

  if (!token) {
    window.location.href = "login.html";
    return;
  }

  const attendanceTableBody = document.querySelector("#attendanceTable tbody");
  const filterDateInput = document.getElementById("filterDate");
  const filterCourseInput = document.getElementById("filterCourse");
  const applyFiltersBtn = document.getElementById("applyFiltersBtn");
  const exportCsvBtn = document.getElementById("exportCsvBtn");

  // Show lecturer-only columns
  if (role === "lecturer") {
    document
      .querySelectorAll(".lecturer-only")
      .forEach((el) => el.classList.remove("d-none"));
  }

  // Default date = today
  if (filterDateInput) {
    filterDateInput.value = new Date().toISOString().slice(0, 10);
  }

  function getHeaders() {
    return {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    };
  }

  function getEndpoint() {
    if (role === "lecturer") return "/attendance/records";
    if (role === "student") return "/attendance/me";
    throw new Error("Unauthorized role");
  }

  async function fetchAttendance() {
    const params = new URLSearchParams();
    if (filterDateInput?.value) params.append("date", filterDateInput.value);
    if (filterCourseInput?.value)
      params.append("course", filterCourseInput.value);

    try {
      const res = await fetch(
        `${API_BASE}${getEndpoint()}?${params.toString()}`,
        { headers: getHeaders() }
      );

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Failed to fetch attendance");
      }

      return await res.json();
    } catch (err) {
      showAlert(err.message, "danger");
      return [];
    }
  }

  function populateTable(records = []) {
    attendanceTableBody.innerHTML = "";

    if (!records.length) {
      attendanceTableBody.innerHTML = `
      <tr>
        <td colspan="7" class="text-center text-muted py-4">
          No attendance records found.
        </td>
      </tr>`;
      return;
    }

    records.forEach((r, idx) => {
      const tr = document.createElement("tr");

      tr.innerHTML = `
      <td>${idx + 1}</td>
      ${
        role === "lecturer"
          ? `
        <td>${escapeHtml(r.student_name || "")}</td>
        <td>${escapeHtml(r.registration_number || "")}</td>
        <td>${escapeHtml(r.department || "")}</td>`
          : ""
      }
      <td>${escapeHtml(r.course_code || "")}</td>
      <td>${formatDate(r.date)}</td>
      <td>${statusBadge(r.status)}</td>
    `;

      attendanceTableBody.appendChild(tr);
    });
  }

  async function applyFilters() {
    showAlert("Loading attendance...", "info", 1200);
    const data = await fetchAttendance();
    populateTable(data);
  }

  function exportToCSV() {
    const rows = attendanceTableBody.querySelectorAll("tr");
    if (!rows.length) {
      showAlert("Nothing to export", "warning");
      return;
    }

    let csv = [];
    const headers = Array.from(
      document.querySelectorAll("#attendanceTable thead th")
    ).map((h) => `"${h.textContent.trim()}"`);
    csv.push(headers.join(","));

    rows.forEach((row) => {
      const cols = Array.from(row.children).map(
        (c) => `"${c.textContent.trim().replace(/"/g, '""')}"`
      );
      csv.push(cols.join(","));
    });

    const blob = new Blob([csv.join("\n")], { type: "text/csv" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = `attendance_${role}.csv`;
    a.click();

    URL.revokeObjectURL(url);
  }

  function statusBadge(status) {
    if (status === "present")
      return `<span class="status-badge status-present">Present</span>`;
    if (status === "absent")
      return `<span class="status-badge status-absent">Absent</span>`;
    return `<span class="badge bg-secondary">${status}</span>`;
  }

  function formatDate(dateStr) {
    return new Date(dateStr).toLocaleDateString();
  }

  function escapeHtml(text) {
    return String(text)
      .replaceAll("&", "&")
      .replaceAll("<", "<")
      .replaceAll(">", ">");
  }

  function showAlert(msg, type = "info", timeout = 2500) {
    const alert = document.createElement("div");
    alert.className = `alert alert-${type} position-fixed top-0 start-50 translate-middle-x mt-3`;
    alert.style.zIndex = "1055";
    alert.textContent = msg;
    document.body.appendChild(alert);
    setTimeout(() => alert.remove(), timeout);
  }

  applyFiltersBtn?.addEventListener("click", applyFilters);
  exportCsvBtn?.addEventListener("click", exportToCSV);

  applyFilters();
});
