// Caching helper — TTL: 1 hour
const CACHE_TTL_MS = 60 * 60 * 1000;

async function request(endpoint, options = {}) {
  const token = frappe?.csrf_token || document.cookie
    .match(/CSRFToken=([^;]+)/)?.[1];

  const headers = {
    "Content-Type": "application/json",
    Accept: "application/json",
    ...options.headers,
  };

  if (options.method && options.method !== "GET" && token) {
    headers["X-Frappe-CSRF-Token"] = token;
  }

  const res = await fetch(`/api/method/${endpoint}`, {
    ...options,
    headers,
    credentials: "include",
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    let msg = "Request failed";
    if (err._server_messages) {
      try {
        const msgs = JSON.parse(err._server_messages);
        msg = JSON.parse(msgs[0]).message || msg;
      } catch {
        /* ignore */
      }
    } else if (err.exception) {
      msg = err.exception;
    }
    throw new Error(msg);
  }

  const data = await res.json();
  return data.message !== undefined ? data.message : data;
}

function get(endpoint) {
  return request(endpoint, { method: "GET" });
}

function post(endpoint, body) {
  return request(endpoint, {
    method: "POST",
    body: body ? JSON.stringify(body) : undefined,
  });
}

/**
 * useCachedFetch — TTL: 1 hour
 * 1. Try cache (with expiry check)
 * 2. Fetch fresh
 * 3. Update cache
 */
export function useCachedFetch(key, fetcher, onData) {
  // 1. Try cache (with expiry check)
  const cached = localStorage.getItem(`cache_${key}`);
  if (cached) {
    try {
      const { data, timestamp } = JSON.parse(cached);
      const isExpired = Date.now() - timestamp > CACHE_TTL_MS;
      if (!isExpired) {
        onData(data);
      } else {
        localStorage.removeItem(`cache_${key}`);
      }
    } catch (e) {
      console.warn("Cache parse error", key);
      localStorage.removeItem(`cache_${key}`);
    }
  }

  // 2. Fetch fresh
  fetcher()
    .then((freshData) => {
      onData(freshData);
      // 3. Update cache
      localStorage.setItem(
        `cache_${key}`,
        JSON.stringify({ data: freshData, timestamp: Date.now() })
      );
    })
    .catch((e) => {
      console.error("Fetch failed", key, e);
      // If we had no cache, propagate error? Or just silent fail?
      // user wants "offline" behavior, so silent fail if we have cache is good.
      if (!cached) throw e;
    });
}

// ---------- Leave ----------
export const leaveApi = {
  getBalance: () => get("zervar_core.api.attendance.get_leave_balance"),
  getApplications: () => get("zervar_core.api.attendance.get_leave_applications"),
  getTypes: () => get("zervar_core.api.attendance.get_leave_types"),
};

// ---------- Holidays ----------
export const holidayApi = {
  getMonthHolidays: (from_date, to_date) => {
    const params = new URLSearchParams();
    if (from_date) params.set("from_date", from_date);
    if (to_date) params.set("to_date", to_date);
    const qs = params.toString();
    return get(`zervar_core.api.attendance.get_holidays?${qs}`);
  },
};

// ---------- Attendance / Stats ----------
export const attendanceApi = {
  getTodayCheckin: () => get("zervar_core.api.attendance.get_today_checkin_status"),
  punch: () => post("zervar_core.api.attendance.punch"),
  getMonthStats: () => get("zervar_core.api.attendance.get_month_stats"),
  getSummary: (employee) => get(`zervar_core.api.attendance.get_attendance_summary?employee=${encodeURIComponent(employee)}`),
};

// ---------- Dashboard ----------
export const dashboardApi = {
  getData: () => get("zervar_core.api.attendance.get_dashboard_data"),
  getEmployeeInfo: () => get("zervar_core.api.attendance.get_employee_info"),
};

export const authApi = {
  changePassword: (oldPw, newPw) =>
    post("zervar_core.api.auth.change_password", {
      old_password: oldPw,
      new_password: newPw,
    }),
};

export const rosterApi = {
  getWeeklyStats: (employeeId) =>
    get(`zevar_core.api.roster.get_weekly_roster?employee_id=${encodeURIComponent(employeeId)}`),
};

export default {
  leaveApi,
  holidayApi,
  attendanceApi,
  dashboardApi,
  rosterApi,
  authApi,
  useCachedFetch,
};
