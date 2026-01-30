import { useState, useEffect, useRef } from "react";

const API = "/api";

export default function App() {
  const [file, setFile] = useState(null);
  const [bpm, setBpm] = useState("");
  const [quant, setQuant] = useState("1/16");
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);
  const pollRef = useRef(null);

  async function upload() {
    if (!file) return;
    setError(null);
    setStatus(null);
    setJobId(null);

    const fd = new FormData();
    fd.append("audio", file);
    if (bpm) fd.append("bpm", bpm);
    fd.append("quantization", quant);

    try {
      const res = await fetch(`${API}/upload`, { method: "POST", body: fd });
      if (!res.ok) {
        setError((await res.json()).detail || "Upload failed");
        return;
      }
      const { job_id } = await res.json();
      setJobId(job_id);
    } catch (e) {
      setError(e.message);
    }
  }

  useEffect(() => {
    if (!jobId) return;
    const poll = async () => {
      try {
        const res = await fetch(`${API}/jobs/${jobId}`);
        const data = await res.json();
        setStatus(data);
        if (data.status === "done" || data.status === "error") {
          clearInterval(pollRef.current);
          if (data.status === "error") setError(data.error);
        }
      } catch {}
    };
    poll();
    pollRef.current = setInterval(poll, 1000);
    return () => clearInterval(pollRef.current);
  }, [jobId]);

  const outputs = status?.outputs || {};

  return (
    <div style={{ maxWidth: 560, margin: "40px auto", fontFamily: "system-ui" }}>
      <h1>PianoTranspose</h1>
      <p>Upload a solo piano recording to get sheet music.</p>

      <div style={{ marginBottom: 12 }}>
        <input type="file" accept=".wav,.mp3,.flac,.ogg" onChange={(e) => setFile(e.target.files[0])} />
      </div>

      <div style={{ display: "flex", gap: 12, marginBottom: 12 }}>
        <label>
          BPM (optional):
          <input type="number" value={bpm} onChange={(e) => setBpm(e.target.value)} style={{ width: 60, marginLeft: 4 }} />
        </label>
        <label>
          Quantization:
          <select value={quant} onChange={(e) => setQuant(e.target.value)} style={{ marginLeft: 4 }}>
            <option value="1/16">1/16</option>
            <option value="1/8">1/8</option>
          </select>
        </label>
      </div>

      <button onClick={upload} disabled={!file}>Upload &amp; Transcribe</button>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {status && (
        <div style={{ marginTop: 20 }}>
          <p>Status: <strong>{status.status}</strong> &mdash; {status.progress}%</p>
          <progress value={status.progress} max={100} style={{ width: "100%" }} />
        </div>
      )}

      {status?.status === "done" && (
        <div style={{ marginTop: 16, display: "flex", gap: 8 }}>
          {outputs.midi_url && <a href={outputs.midi_url} download><button>Download MIDI</button></a>}
          {outputs.musicxml_url && <a href={outputs.musicxml_url} download><button>Download MusicXML</button></a>}
          {outputs.pdf_url && <a href={outputs.pdf_url} download><button>Download PDF</button></a>}
        </div>
      )}
    </div>
  );
}
