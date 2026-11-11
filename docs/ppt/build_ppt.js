// Rebuild with: node build_ppt.js   (needs: npm i pptxgenjs)
const pptxgen = require("pptxgenjs");
const SKILL = process.env.PPTX_SKILL_DIR || "/mnt/skills/public/pptx";
let applyTheme = null;
try { applyTheme = require(SKILL + "/scripts/apply_theme.js").applyTheme; } catch (e) { /* theme colours then use Office defaults */ }

const THEME = {
  name: "AgriMind", headFontFace: "Trebuchet MS", bodyFontFace: "Calibri",
  colors: { dk1: "1B2822", lt1: "FFFFFF", dk2: "1D4A38", lt2: "F1F3EC", accent1: "1D4A38", accent2: "E0A21B",
            accent3: "2F6E92", accent4: "AF3B2E", accent5: "4C9A6B", accent6: "9AA89F", hlink: "2F6E92", folHlink: "5D6C64" },
};
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.title = "AgriMind Fusion";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;

pres.defineSlideMaster({
  title: "TITLE_DARK", background: { color: C.accent1 },
  objects: [], slideNumber: undefined,
});
pres.defineSlideMaster({
  title: "CONTENT", background: { color: C.background2 },
  objects: [{ rect: { x: 0, y: 5.3, w: 10, h: 0.325, fill: { color: C.accent1 } } },
            { text: { text: "AgriMind Fusion | B.Tech CSE (AI & ML) major project", options: { x: 0.5, y: 5.3, w: 6, h: 0.325, fontSize: 9, color: C.background1, isTextBox: true } } }],
  slideNumber: { x: 9.2, y: 5.3, w: 0.5, h: 0.325, color: C.background1, fontSize: 9 },
});

const body = (s, text, o) => s.addText(text, Object.assign({ isTextBox: true, fontSize: 14, color: C.text1, valign: "top", margin: 0 }, o));
const card = (s, x, y, w, h, head, txt, accent, name, fs) => {
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, fill: { color: C.background1 }, line: { color: C.accent6, width: 0.75 }, rectRadius: 0.08, objectName: name || head });
  s.addShape(pres.ShapeType.rect, { x, y: y + 0.12, w: 0.07, h: h - 0.24, fill: { color: accent || C.accent1 }, line: { color: accent || C.accent1, width: 0 } });
  body(s, head, { x: x + 0.25, y: y + 0.12, w: w - 0.4, h: 0.35, fontSize: 15, bold: true, color: C.accent1 });
  body(s, txt, { x: x + 0.25, y: y + 0.55, w: w - 0.4, h: h - 0.65, fontSize: fs || 13.5 });
};
let first = true;
const content = (title, section) => {
  if (section) pres.addSection({ title: section });
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: section || currentSection });
  if (section) currentSection = section;
  s.addText(title, { x: 0.5, y: 0.3, w: 9, h: 0.75, fontSize: 26, bold: true, color: C.accent1, fontFace: "Trebuchet MS", valign: "middle", margin: 0, isTextBox: true });
  return s;
};
let currentSection = "Introduction";

// 1 Title
pres.addSection({ title: "Introduction" });
let s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: "Introduction" });
s.addText("AgriMind Fusion", { x: 0.7, y: 1.3, w: 8.6, h: 1, fontSize: 44, bold: true, color: C.background1, fontFace: "Trebuchet MS", isTextBox: true, margin: 0 });
body(s, "Context-Aware AI for Crop Stress Detection and Explainable Agricultural Decision Support", { x: 0.7, y: 2.4, w: 7.8, h: 0.9, fontSize: 20, color: C.background2 });
s.addShape(pres.ShapeType.rect, { x: 0.7, y: 3.55, w: 1.2, h: 0.06, fill: { color: C.accent2 }, line: { color: C.accent2, width: 0 } });
body(s, "B.Tech CSE (AI & ML) Major Project\nTeam: [Member 1], [Member 2], [Member 3]   Guide: [Name]", { x: 0.7, y: 3.8, w: 8, h: 0.8, fontSize: 14, color: C.background2 });
s.addNotes("Introduce the team and the one-line idea: a leaf-disease classifier that explains itself and shows environmental context without pretending to be something it is not.");

// 2 Problem
s = content("Why this problem matters");
card(s, 0.5, 1.3, 2.9, 3.6, "Diseases cost yield", "Late blight, bacterial spot and viruses can spread fast. Small farmers often cannot reach an expert quickly.", C.accent4, "Problem card 1", 16);
card(s, 3.55, 1.3, 2.9, 3.6, "Black-box predictions", "Most leaf-disease apps return a label only. Users cannot tell whether the model looked at the leaf or the background.", C.accent2, "Problem card 2", 16);
card(s, 6.6, 1.3, 2.9, 3.6, "Lab vs field gap", "Popular datasets use plain backgrounds. Accuracy on real field photos is usually lower, and rarely reported honestly.", C.accent3, "Problem card 3", 16);
s.addNotes("Frame the three gaps this project addresses: speed of access, explainability, and generalisation.");

// 3 Objectives
s = content("Objectives");
body(s, [
  { text: "Compare a baseline CNN with MobileNetV2 transfer learning (CPU-friendly)", options: { bullet: true, breakLine: true } },
  { text: "Evaluate with accuracy, precision, recall, F1 and confusion matrices", options: { bullet: true, breakLine: true } },
  { text: "Test generalisation on real field images (PlantDoc, overlapping classes)", options: { bullet: true, breakLine: true } },
  { text: "Explain predictions with Grad-CAM", options: { bullet: true, breakLine: true } },
  { text: "Add Open-Meteo weather context through a rule-based risk engine and what-if simulator", options: { bullet: true, breakLine: true } },
  { text: "Deliver a working React + FastAPI web app with history, analytics and PDF reports", options: { bullet: true } },
], { x: 0.5, y: 1.3, w: 9, h: 3.6, fontSize: 16, paraSpaceAfter: 8 });

// 4 Honest scope
s = content("What each data source does, and does not do");
card(s, 0.5, 1.3, 2.9, 2.7, "PlantVillage", "Labelled leaf images. Trains and tests the classifier. The only data the CNN learns from.", C.accent1, "Source card 1");
card(s, 3.55, 1.3, 2.9, 2.7, "Open-Meteo weather", "Current, forecast and historical weather. Feeds a rule-based risk engine. Never an input to the CNN.", C.accent3, "Source card 2");
card(s, 6.6, 1.3, 2.9, 2.7, "Sentinel-2 (optional)", "NDVI and NDMI for a field area through Earth Engine. A vegetation indicator, not a leaf diagnosis.", C.accent5, "Source card 3");
body(s, "No trained multimodal model is claimed: PlantVillage images have no matching weather or satellite records.", { x: 0.5, y: 4.3, w: 9, h: 0.6, fontSize: 14, bold: true, color: C.accent4 });
s.addNotes("This is the integrity slide. Examiners should hear it from us first.");

// 5 Architecture
s = content("System architecture", "System");
const box = (x, y, w, h, t, sub, fill, txtc) => {
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, fill: { color: fill }, line: { color: fill, width: 0 }, rectRadius: 0.08, objectName: t });
  body(s, [{ text: t, options: { bold: true, fontSize: 13, breakLine: true } }, { text: sub, options: { fontSize: 10.5 } }], { x: x + 0.1, y: y + 0.1, w: w - 0.2, h: h - 0.2, color: txtc, valign: "middle", align: "center" });
};
const arrow = (x1, y, x2) => s.addShape(pres.ShapeType.line, { x: x1, y, w: x2 - x1, h: 0, line: { color: C.accent6, width: 2, endArrowType: "triangle" } });
box(0.4, 1.35, 1.7, 2.9, "Input", "Leaf photo\nCrop (optional)\nTemperature, humidity, rain, soil (optional)", C.accent6, C.text1);
box(2.6, 1.35, 2.6, 1.3, "Vision AI", "MobileNetV2 classifier + Grad-CAM", C.accent1, C.background1);
box(2.6, 2.95, 2.6, 1.3, "Context engine", "Open-Meteo + documented risk rules", C.accent3, C.background1);
box(5.7, 1.35, 1.8, 2.9, "Decision support", "Prediction, confidence and risk shown separately; recommendations traced to inputs", C.accent2, C.text1);
box(7.9, 1.35, 1.7, 2.9, "Web app", "React dashboard\nFastAPI\nSQLite / PostgreSQL\nPDF report", C.accent1, C.background1);
arrow(2.1, 2.0, 2.6); arrow(2.1, 3.6, 2.6); arrow(5.2, 2.0, 5.7); arrow(5.2, 3.6, 5.7); arrow(7.5, 2.8, 7.9);
body(s, "Image prediction and environmental context stay separate end to end. Weather never changes the CNN output.", { x: 0.5, y: 4.55, w: 9, h: 0.5, fontSize: 13, bold: true, color: C.accent1 });

// 6 Datasets
s = content("Datasets");
const hdr = (t) => ({ text: t, options: { bold: true, color: C.background1, fill: { color: C.accent1 } } });
s.addTable([
  [hdr("Dataset"), hdr("Role"), hdr("Linked to the CNN?")],
  ["PlantVillage (Kaggle: emmarex/plantdisease)", "15 classes: tomato 10, potato 3, bell pepper 2. Training, validation, test (70/15/15, seed 42)", "Yes"],
  ["PlantDoc", "Field images for the generalisation test, mapped classes only", "Evaluation only"],
  ["Open-Meteo", "Forecast and archive weather, soil moisture estimate", "No"],
  ["Sentinel-2 SR Harmonized", "NDVI and NDMI indicators via Google Earth Engine", "No"],
], { x: 0.5, y: 1.3, w: 9, colW: [3, 4.4, 1.6], fontSize: 12, color: C.text1, border: { type: "solid", pt: 0.5, color: C.accent6 }, fill: { color: C.background1 }, valign: "middle", margin: 0.08 });
body(s, "Cleaning: integrity check, MD5 de-duplication, label-conflict removal. Limitation: no leaf IDs, so near-duplicates may cross splits.", { x: 0.5, y: 4.3, w: 9, h: 0.7, fontSize: 12, color: C.accent4 });

// 7 Pipeline
s = content("Model pipeline", "Method");
const steps = [["Validate + split", "Corrupt and duplicate files removed; stratified 70/15/15"], ["Augment", "Flips, rotation, zoom, contrast (train only)"], ["Baseline CNN", "4 conv blocks, 224x224 RGB"], ["MobileNetV2", "ImageNet weights, frozen then fine-tuned"], ["Evaluate", "Test set + field images"]];
steps.forEach((st, i) => {
  const x = 0.5 + i * 1.82;
  s.addShape(pres.ShapeType.roundRect, { x, y: 1.5, w: 1.62, h: 2.2, fill: { color: i === 3 ? C.accent1 : C.background1 }, line: { color: C.accent1, width: 1 }, rectRadius: 0.08, objectName: `Step ${i + 1}` });
  body(s, [{ text: st[0], options: { bold: true, fontSize: 13, breakLine: true } }, { text: st[1], options: { fontSize: 10.5 } }], { x: x + 0.1, y: 1.6, w: 1.42, h: 2, color: i === 3 ? C.background1 : C.text1 });
});
body(s, "CPU-only training: small input size, pretrained backbone, early stopping, checkpointing. Same split and augmentation for both models so the comparison is fair.", { x: 0.5, y: 4.0, w: 9, h: 0.9, fontSize: 13 });

// 8 Grad-CAM
s = content("Explainable AI with Grad-CAM");
body(s, [
  { text: "Highlights the image regions that raised the score of the predicted class", options: { bullet: true, breakLine: true } },
  { text: "Computed on the last MobileNetV2 feature map from the pre-softmax logit", options: { bullet: true, breakLine: true } },
  { text: "App shows a slider that reveals the heatmap over the leaf", options: { bullet: true, breakLine: true } },
  { text: "Region summary is computed from the heatmap (where, and how much of the image)", options: { bullet: true } },
], { x: 0.5, y: 1.3, w: 5.2, h: 3.3, fontSize: 15, paraSpaceAfter: 8 });
card(s, 6.0, 1.3, 3.5, 3.3, "Read it carefully", "Grad-CAM shows where the model looked. It does not prove the biological cause. Attention on the background is a warning sign. Confidence is a softmax score, not a calibrated probability.", C.accent2, "Caution card", 15);

// 9 Risk engine
s = content("Rule-based environmental risk engine");
s.addTable([
  [hdr("Factor"), hdr("Condition"), hdr("Points")],
  ["Humidity", ">= 85%  /  70 to 84%", "+2  /  +1"],
  ["Temperature", "15 to 28 C", "+1"],
  ["Rainfall", ">= 15 mm per day  /  5 to 14 mm", "+2  /  +1"],
  ["Soil moisture", ">= 0.40 m3/m3 (waterlogged)", "+1"],
  ["Category", "0 to 1 Low, 2 to 3 Moderate, 4 to 6 High", ""],
], { x: 0.5, y: 1.3, w: 5.6, colW: [1.5, 3.1, 1.0], fontSize: 12, color: C.text1, border: { type: "solid", pt: 0.5, color: C.accent6 }, fill: { color: C.background1 }, valign: "middle", margin: 0.08 });
card(s, 6.4, 1.3, 3.1, 3.5, "Honest label", "Generic rules of thumb with an explanation for every point awarded. Not validated against disease outcomes and never used to change the image prediction. The what-if simulator re-runs only these rules.", C.accent2, "Rule caution", 14);

// 10 Modules
s = content("Application modules", "System");
const mods = [["Crop Doctor", "Upload, predict, top 3, Grad-CAM"], ["Weather", "Search, 7-day forecast, history"], ["Risk simulator", "Sliders, before/after rules"], ["Recommendations", "Traceable, no pesticide doses"], ["Scan history", "Search, filter, compare, delete"], ["Analytics", "Charts and CSV export"], ["Assistant", "Rule-based, scan-aware"], ["PDF report", "Prediction, Grad-CAM, limits"]];
mods.forEach((m, i) => card(s, 0.5 + (i % 4) * 2.28, 1.3 + Math.floor(i / 4) * 1.85, 2.13, 1.65, m[0], m[1], i % 2 ? C.accent3 : C.accent1, `Module ${m[0]}`));
body(s, "Satellite NDVI/NDMI is an optional module that needs an Earth Engine account.", { x: 0.5, y: 5.0, w: 9, h: 0.25, fontSize: 11, color: C.accent4 });

// 11 Tech
s = content("Technology stack");
s.addTable([
  [hdr("Layer"), hdr("Tools")],
  ["AI / ML", "Python 3.12, TensorFlow/Keras (MobileNetV2), OpenCV, NumPy, Pandas, scikit-learn, Matplotlib"],
  ["Backend", "FastAPI, Pydantic, SQLAlchemy, ReportLab, httpx"],
  ["Frontend", "React, Vite, React Router, Recharts, Lucide icons"],
  ["Data", "SQLite (local), PostgreSQL (deployment), uploaded images on disk"],
  ["External", "Open-Meteo API, Google Earth Engine (optional), Docker"],
], { x: 0.5, y: 1.3, w: 9, colW: [1.8, 7.2], fontSize: 13, color: C.text1, border: { type: "solid", pt: 0.5, color: C.accent6 }, fill: { color: C.background1 }, valign: "middle", margin: 0.1 });

// 12 Evaluation plan
s = content("Evaluation plan and results", "Evaluation");
s.addTable([
  [hdr("Model"), hdr("Test accuracy"), hdr("Macro F1"), hdr("Field-image accuracy"), hdr("CPU ms per image")],
  ["Baseline CNN", "pending", "pending", "pending", "pending"],
  ["MobileNetV2", "pending", "pending", "pending", "pending"],
], { x: 0.5, y: 1.3, w: 9, colW: [2.2, 1.7, 1.5, 2.0, 1.6], fontSize: 13, color: C.text1, border: { type: "solid", pt: 0.5, color: C.accent6 }, fill: { color: C.background1 }, valign: "middle", margin: 0.1, align: "center" });
body(s, "Cells say pending on purpose: no training results exist yet. Replace them with the values in models/metrics/comparison.csv after running scripts/evaluate.py.", { x: 0.5, y: 2.9, w: 9, h: 0.6, fontSize: 13, bold: true, color: C.accent4 });
body(s, [
  { text: "Also reported: per-class precision/recall/F1, confusion matrices, training curves", options: { bullet: true, breakLine: true } },
  { text: "Key question: how large is the drop from lab photos to field photos?", options: { bullet: true, breakLine: true } },
  { text: "Qualitative Grad-CAM study of correct and wrong predictions", options: { bullet: true } },
], { x: 0.5, y: 3.6, w: 9, h: 1.4, fontSize: 13, paraSpaceAfter: 5 });
s.addNotes("Do not present this slide until real numbers are inserted.");

// 13 Limitations
s = content("Limitations and responsible use", "Wrap-up");
card(s, 0.5, 1.3, 4.35, 1.75, "Model", "Only 15 classes and 3 crops. Controlled-background training data. Softmax confidence is not calibrated.", C.accent4, "Limit model");
card(s, 5.15, 1.3, 4.35, 1.75, "Context", "Weather is area data, soil moisture is an estimate, rules are unvalidated. Satellite values describe a field, not a leaf.", C.accent3, "Limit context");
card(s, 0.5, 3.2, 4.35, 1.75, "Advice", "General guidance without pesticide doses. Confirm with a local agricultural extension officer.", C.accent2, "Limit advice");
card(s, 5.15, 3.2, 4.35, 1.75, "System", "No user accounts, no migrations, deployment untested until verified, assistant is rule-based.", C.accent6, "Limit system");

// 14 Plan
s = content("Team and 4-day plan");
const days = [["Day 1", "Environment, data validation, training"], ["Day 2", "Evaluation, Grad-CAM, API"], ["Day 3", "Frontend, context engine, history"], ["Day 4", "Testing, report, docs, optional satellite"]];
days.forEach((d, i) => card(s, 0.5 + i * 2.28, 1.3, 2.13, 1.9, d[0], d[1], C.accent1, `Plan ${d[0]}`));
body(s, [
  { text: "Member 1: dataset, models, evaluation, Grad-CAM", options: { bullet: true, breakLine: true } },
  { text: "Member 2: weather, risk rules, knowledge base, satellite, research writing", options: { bullet: true, breakLine: true } },
  { text: "Member 3: frontend, backend integration, database, reports, deployment", options: { bullet: true } },
], { x: 0.5, y: 3.5, w: 9, h: 1.4, fontSize: 14, paraSpaceAfter: 6 });

// 15 Future / demo
s = content("Demo flow and future work");
body(s, [
  { text: "Demo: upload leaf, show prediction and Grad-CAM, add weather, change simulator sliders, open history, download PDF", options: { bullet: true, breakLine: true } },
  { text: "Future: collect aligned image + weather data for real multimodal learning", options: { bullet: true, breakLine: true } },
  { text: "Future: probability calibration, more crops, regional languages, expert-reviewed knowledge base", options: { bullet: true, breakLine: true } },
  { text: "Future: field trials with farmers and agronomists", options: { bullet: true } },
], { x: 0.5, y: 1.3, w: 9, h: 3.4, fontSize: 16, paraSpaceAfter: 10 });

(async () => {
  const f = "AgriMind_Fusion_Presentation.pptx";
  await pres.writeFile({ fileName: f });
  if (applyTheme) await applyTheme(f, THEME);
  console.log("written", f);
})();
