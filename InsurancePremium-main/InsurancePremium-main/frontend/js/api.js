/* ==========================================================================
   api.js
   --------------------------------------------------------------------------
   Small wrapper around the Fetch API for talking to the FastAPI backend.
   Every function returns a Promise that resolves with parsed JSON, or
   throws an Error with a human-readable message on failure.
   ========================================================================== */

const API_BASE = "http://localhost:8000";

/**
 * Internal helper: performs a fetch call and throws a readable error
 * (using the backend's "detail" message) if the response is not OK.
 */
async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options);

  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      if (body && body.detail) message = body.detail;
    } catch (err) {
      // response wasn't JSON — keep the generic message
    }
    throw new Error(message);
  }

  return response.json();
}

async function predictOne(record) {
  return request("/api/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(record),
  });
}
