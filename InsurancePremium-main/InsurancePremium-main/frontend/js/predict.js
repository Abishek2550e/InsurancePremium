/* ==========================================================================
   predict.js
   --------------------------------------------------------------------------
   Logic for the "Predict Premium" page (index.html):
     - Live BMI preview as the user types height/weight
     - Client-side form validation with inline error messages
     - Calls POST /api/predict and renders the result card + gauge chart
     - CSV download (built entirely in the browser)
   ========================================================================== */

const form = document.getElementById("predict-form");
const submitBtn = document.getElementById("predict-submit-btn");
const submitLabel = document.getElementById("predict-submit-label");
const resultAlertArea = document.getElementById("result-alert-area");
const resultPanel = document.getElementById("result-panel");
const resultPlaceholder = document.getElementById("result-placeholder");
const bmiPreviewValue = document.getElementById("bmi-preview-value");

let lastRecord = null;
let lastResult = null;

const SVG_NS = "http://www.w3.org/2000/svg";

/** Creates an SVG element with the given tag and attributes. */
function createSvgElement(tag, attrs = {}) {
  const el = document.createElementNS(SVG_NS, tag);
  Object.entries(attrs).forEach(([key, value]) => el.setAttribute(key, value));
  return el;
}

/** Draws a semicircle "gauge" chart (used for the model confidence score). */
function drawGauge(container, { value, color = "#4f46e5" }) {
  container.innerHTML = "";
  const wrap = document.createElement("div");
  wrap.className = "gauge-wrap";

  const width = 240;
  const height = 130;
  const cx = width / 2;
  const cy = height - 10;
  const radius = 100;

  const percent = Math.max(0, Math.min(100, value)) / 100;
  const angle = Math.PI - percent * Math.PI; // from 180deg (left) to 0deg (right)
  const endX = cx + radius * Math.cos(angle);
  const endY = cy - radius * Math.sin(angle);
  const largeArc = percent > 0.5 ? 1 : 0;

  const svg = createSvgElement("svg", {
    class: "chart-svg", viewBox: `0 0 ${width} ${height}`, preserveAspectRatio: "xMidYMid meet",
  });

  svg.appendChild(createSvgElement("path", {
    d: `M ${cx - radius} ${cy} A ${radius} ${radius} 0 0 1 ${cx + radius} ${cy}`,
    fill: "none", stroke: "var(--color-border)", "stroke-width": 18, "stroke-linecap": "round",
  }));

  if (percent > 0) {
    svg.appendChild(createSvgElement("path", {
      d: `M ${cx - radius} ${cy} A ${radius} ${radius} 0 ${largeArc} 1 ${endX} ${endY}`,
      fill: "none", stroke: color, "stroke-width": 18, "stroke-linecap": "round",
    }));
  }

  wrap.appendChild(svg);

  const valueLabel = document.createElement("div");
  valueLabel.className = "gauge-value";
  valueLabel.textContent = `${value}%`;
  wrap.appendChild(valueLabel);

  container.appendChild(wrap);
}

/** Computes BMI = weight(kg) / height(m)^2, rounded to 2 decimals. */
function computeBmi(heightCm, weightKg) {
  const heightM = heightCm / 100;
  if (!heightM) return 0;
  return Math.round((weightKg / (heightM * heightM)) * 100) / 100;
}

function updateBmiPreview() {
  const height = Number(document.getElementById("height").value);
  const weight = Number(document.getElementById("weight").value);
  bmiPreviewValue.textContent = computeBmi(height, weight);
}

function bmiCategory(bmi) {
  if (bmi < 18.5) return "Underweight";
  if (bmi < 25) return "Normal";
  if (bmi < 30) return "Overweight";
  return "Obese";
}

/** Clears all inline field errors. */
function clearFieldErrors() {
  document.querySelectorAll(".field-error").forEach((el) => (el.textContent = ""));
  document.querySelectorAll(".form-field input, .form-field select").forEach((el) => el.classList.remove("invalid"));
}

function setFieldError(fieldId, message) {
  const input = document.getElementById(fieldId);
  const errorEl = document.getElementById(`${fieldId}-error`);
  if (input) input.classList.add("invalid");
  if (errorEl) errorEl.textContent = message;
}

/**
 * Validates the form values in the browser before calling the API.
 * Returns an array of { fieldId, message } — empty array means valid.
 */
function validateForm(values) {
  const errors = [];
  if (!(values.age >= 18 && values.age <= 100)) {
    errors.push({ fieldId: "age", message: "Age must be between 18 and 100." });
  }
  if (!(values.height >= 50 && values.height <= 250)) {
    errors.push({ fieldId: "height", message: "Height must be between 50 and 250 cm." });
  }
  if (!(values.weight >= 10 && values.weight <= 300)) {
    errors.push({ fieldId: "weight", message: "Weight must be between 10 and 300 kg." });
  }
  if (!(values.children >= 0 && values.children <= 10)) {
    errors.push({ fieldId: "children", message: "Children must be between 0 and 10." });
  }
  return errors;
}

function readFormValues() {
  return {
    age: Number(document.getElementById("age").value),
    gender: document.getElementById("gender").value,
    height: Number(document.getElementById("height").value),
    weight: Number(document.getElementById("weight").value),
    smoker: document.getElementById("smoker").value,
    children: Number(document.getElementById("children").value),
    region: document.getElementById("region").value,
  };
}

function showAlert(message, variant = "error") {
  const iconByVariant = { error: "x-circle", warning: "alert-triangle", info: "info" };
  resultAlertArea.innerHTML = `
    <div class="alert alert-${variant}">
      ${svgIcon(iconByVariant[variant] || "info", 18)}
      <span>${message}</span>
    </div>
  `;
}

function clearAlert() {
  resultAlertArea.innerHTML = "";
}

function setLoading(isLoading) {
  submitBtn.disabled = isLoading;
  submitLabel.textContent = isLoading ? "Predicting…" : "Predict Premium";
  document.getElementById("submit-icon").innerHTML = isLoading
    ? '<span class="spinner"></span>'
    : svgIcon("sparkles", 18);
}

function renderResult(record, result) {
  resultPlaceholder.classList.add("hidden");
  resultPanel.classList.remove("hidden");

  resultPanel.innerHTML = `
    <div class="result-hero">
      <div class="result-hero-label">${svgIcon("shield", 14)} Predicted Annual Premium</div>
      <div class="result-hero-value">₹${result.predicted_premium.toLocaleString()}</div>
      <div class="result-hero-sub">Model: ${result.model_used}</div>
    </div>

    <div class="metric-grid" style="margin-bottom:0;">
      <div class="metric-card">
        <div class="metric-info">
          <div class="metric-title">Confidence Score</div>
          <div class="metric-value">${result.confidence}%</div>
          <div class="metric-sub">Based on model R² score</div>
        </div>
        <div class="metric-icon emerald">${svgIcon("check-circle", 20)}</div>
      </div>
      <div class="metric-card">
        <div class="metric-info">
          <div class="metric-title">BMI Category</div>
          <div class="metric-value">${bmiCategory(record.bmi)}</div>
          <div class="metric-sub">BMI = ${record.bmi}</div>
        </div>
        <div class="metric-icon amber">${svgIcon("activity", 20)}</div>
      </div>
    </div>

    <div class="card chart-card">
      <h3>Model Confidence</h3>
      <div id="gauge-container"></div>
    </div>

    <div class="btn-row">
      <button class="btn btn-secondary" id="download-csv-btn">${svgIcon("download", 16)} Download CSV</button>
    </div>
  `;

  drawGauge(document.getElementById("gauge-container"), { value: result.confidence });

  document.getElementById("download-csv-btn").addEventListener("click", () => downloadCsv(record, result));
}

/** Builds a one-row CSV file from the record + result and triggers a download. */
function downloadCsv(record, result) {
  const row = { ...record, ...result };
  const headers = Object.keys(row);
  const csvContent = [headers.join(","), headers.map((h) => row[h]).join(",")].join("\n");
  const blob = new Blob([csvContent], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "premium_prediction.csv";
  link.click();
  URL.revokeObjectURL(url);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearFieldErrors();
  clearAlert();

  const values = readFormValues();
  const errors = validateForm(values);
  if (errors.length > 0) {
    errors.forEach((err) => setFieldError(err.fieldId, err.message));
    showAlert("Please fix the highlighted fields before predicting.", "error");
    return;
  }

  setLoading(true);
  try {
    const result = await predictOne(values);
    lastRecord = { ...values, bmi: result.bmi };
    lastResult = result;
    renderResult(lastRecord, lastResult);
  } catch (err) {
    showAlert(err.message || "Prediction failed. Please try again.", "error");
  } finally {
    setLoading(false);
  }
});

["height", "weight"].forEach((id) => {
  document.getElementById(id).addEventListener("input", updateBmiPreview);
});

updateBmiPreview();
