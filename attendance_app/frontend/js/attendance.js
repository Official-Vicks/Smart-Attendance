// ======================================================
// attendance.js
// Lecturer view: fetch & display attendance records,
// apply filters, and export CSV.
// Folder: frontend/js/
// ======================================================

document.addEventListener("DOMContentLoaded", () => {
  console.log("Attendance JS loaded ✅");

  // Elements
  const attendanceTableBody = document.querySelector("#attendanceTable tbody");
  const filterDateInput = document.getElementById("filterDate");
  const filterDeptSelect = document.getElementById("filterDepartment");
  const applyFiltersBtn = document.getElementById("applyFiltersBtn");

  // Default filter date = today
  if (filterDateInput) {
    const today = new Date().toISOString().slice(0, 10);
    filterDateInput.value = today;
  }

  // Quick role-check (simple client-side guard).
  // In production, enforce role-based auth server-side.
  const userRole = localStorage.getItem("userRole") || null;
  if (userRole && userRole !== "lecturer") {
    showAlert("Access denied: lecturer only page.", "danger");
    // Optional: redirect students away
    // setTimeout(() => window.location.href = "dashboard.html", 1500);
  }

  // --- Fetch attendance from backend (placeholder URL) ---
  async function fetchAttendance({ date, department } = {}) {
    // Build query params
    const params = new URLSearchParams();
    if (date) params.append("date", date);
    if (department) params.append("department", department);

    try {
      // Replace URL with your FastAPI endpoint
      const res = await fetch(
        `http://127.0.0.1:8000/attendance/view?${params.toString()}`,
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("access_token") || ""}`,
          },
        }
      );

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Failed to fetch attendance");
      }

      const data = await res.json();
      return data; // Expecting array of attendance records
    } catch (err) {
      console.error("fetchAttendance error:", err);
      showAlert(`Error fetching attendance: ${err.message}`, "danger");
      return [];
    }
  }

  // --- Populate table with attendance records ---
  function populateTable(records = []) {
    if (!attendanceTableBody) return;
    attendanceTableBody.innerHTML = "";

    if (records.length === 0) {
      attendanceTableBody.innerHTML = `
        <tr><td colspan="6" class="text-center text-muted py-4">No attendance records found.</td></tr>
      `;
      return;
    }

    records.forEach((r, idx) => {
      // r expected fields: student_name, reg_number, department, date, status
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <th scope="row">${idx + 1}</th>
        <td>${escapeHtml(r.student_name || "")}</td>
        <td>${escapeHtml(r.reg_number || "")}</td>
        <td>${escapeHtml(r.department || "")}</td>
        <td>${escapeHtml(formatDate(r.date) || "")}</td>
        <td>${statusBadge(r.status)}</td>
      `;
      attendanceTableBody.appendChild(tr);
    });
  }

  // --- Apply filters: fetch & render ---
  async function applyFilters() {
    const date = filterDateInput?.value || "";
    const department = filterDeptSelect?.value || "";
    showAlert("Loading attendance...", "info", 1200);
    const records = await fetchAttendance({ date, department });
    populateTable(records);
  }

  // --- Export currently visible attendance to CSV ---
  function exportTableToCSV(filename = "attendance.csv") {
    // Grab visible table rows
    const rows = Array.from(attendanceTableBody.querySelectorAll("tr"));
    if (rows.length === 0) {
      showAlert("No records to export.", "warning");
      return;
    }

    const csv = [];
    // Header
    csv.push(
      [
        "#",
        "Student Name",
        "Registration Number",
        "Department",
        "Date",
        "Status",
      ].join(",")
    );

    rows.forEach((row, i) => {
      const cols = Array.from(row.querySelectorAll("th, td")).map((td) => {
        // Remove commas/newlines and wrap field in quotes
        return `"${(td.textContent || "").trim().replace(/"/g, '""')}"`;
      });
      if (cols.length) csv.push(cols.join(","));
    });

    const csvBlob = new Blob([csv.join("\n")], {
      type: "text/csv;charset=utf-8;",
    });
    const url = URL.createObjectURL(csvBlob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    showAlert("Exported CSV successfully.", "success");
  }

  // --- Helpers ---
  function statusBadge(status) {
    // normalize status
    const s = (status || "").toLowerCase();
    if (s === "present") return `<span class="badge bg-success">Present</span>`;
    if (s === "absent") return `<span class="badge bg-danger">Absent</span>`;
    return `<span class="badge bg-secondary">${escapeHtml(
      status || "Unknown"
    )}</span>`;
  }

  function formatDate(dateStr) {
    if (!dateStr) return "";
    // Try to create a Date; handle ISO strings
    const d = new Date(dateStr);
    if (Number.isNaN(d.getTime())) return dateStr;
    return d.toLocaleString();
  }

  // Very small HTML escape helper
  function escapeHtml(text) {
    return String(text)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;");
  }

  // --- Minimal reusable alert (Bootstrap style) ---
  function showAlert(message, type = "info", autoCloseMs = 3000) {
    // Remove existing
    const existing = document.querySelector(".custom-alert");
    if (existing) existing.remove();

    const alertDiv = document.createElement("div");
    alertDiv.className = `alert alert-${type} alert-dismissible fade show custom-alert position-fixed top-0 start-50 translate-middle-x mt-3 shadow`;
    alertDiv.style.zIndex = "1055";
    alertDiv.style.width = "90%";
    alertDiv.style.maxWidth = "540px";
    alertDiv.role = "alert";
    alertDiv.innerHTML = `
      <div class="d-flex justify-content-between align-items-center">
        <div class="fw-semibold">${message}</div>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      </div>
    `;
    document.body.appendChild(alertDiv);

    if (autoCloseMs > 0) {
      setTimeout(() => {
        alertDiv.classList.remove("show");
        alertDiv.classList.add("fade");
        setTimeout(() => alertDiv.remove(), 300);
      }, autoCloseMs);
    }
  }

  // --- Event listeners ---
  applyFiltersBtn?.addEventListener("click", (e) => {
    e.preventDefault();
    applyFilters();
  });

  // Export on double-click of table header (or you can create a dedicated button)
  const attendanceTable = document.getElementById("attendanceTable");
  attendanceTable?.querySelector("thead")?.addEventListener("dblclick", (e) => {
    e.preventDefault();
    exportTableToCSV(`attendance_${filterDateInput?.value || "all"}.csv`);
  });

  // Load initial data
  applyFilters();
});
