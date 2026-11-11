export default function About() {
  return (
    <div>
      <div className="page-head"><h1>About and limits</h1><p>AgriMind Fusion is a B.Tech research and learning project. Read this before trusting any output.</p></div>
      <section className="panel"><h3>Model output<span className="tag">Model output</span></h3><p>A MobileNetV2 network (ImageNet weights, fine-tuned on PlantVillage) classifies a leaf photo into 15 classes. Scores are softmax values, not calibrated probabilities. PlantVillage photos are taken on plain backgrounds in controlled light, so accuracy on real field photos is expected to be lower; the project's report measures this gap on a separate field dataset.</p></section>
      <section className="panel"><h3>Grad-CAM<span className="tag">Model output</span></h3><p>Shows where the model looked. It does not prove the biological cause of a disease.</p></section>
      <section className="panel env"><h3>Weather<span className="tag">Your inputs</span></h3><p>Open-Meteo values describe an area (and soil moisture is a model estimate). PlantVillage images were not photographed with matched weather records, so weather is never an input to the image model and the project does not claim a trained multimodal model.</p></section>
      <section className="panel rule"><h3>Risk level<span className="tag">Rule-based</span></h3><p>A short list of documented thresholds adds points for humidity, temperature band, rain and wet soil. The thresholds are generic rules of thumb and were not validated against disease outcomes.</p></section>
      <section className="panel"><h3>Satellite<span className="tag">Indicator</span></h3><p>Sentinel-2 NDVI and NDMI describe vegetation and moisture of an area, not leaf-level disease.</p></section>
      <section className="panel guide"><h3>Recommendations<span className="tag">General guidance</span></h3><p>The advice comes from a small hand-written knowledge base without pesticide doses. Confirm with a local agricultural extension officer. It is not a diagnosis and cannot guarantee results.</p></section>
      <p className="small muted">The coloured edge on each panel shows its source: green for model output, blue for your inputs, yellow for rule-based assessment, dark for general guidance.</p>
    </div>
  );
}
