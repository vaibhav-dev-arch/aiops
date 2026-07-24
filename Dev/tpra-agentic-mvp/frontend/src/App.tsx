import React, { useEffect, useState } from "react";
import { api, Role } from "./api/client";
import "./styles.css";

type Workspace = { id: string; name: string; description: string };
type Agent = { id: string; name: string; description: string };
type FileMeta = { id: string; filename: string; size: number };
type AuditEvent = { id: string; action: string; actor: string; created_at: string };

export default function App() {
  const [role, setRole] = useState<Role>("admin");
  const opts = { role };
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [selected, setSelected] = useState<string>("");
  const [agents, setAgents] = useState<Agent[]>([]);
  const [files, setFiles] = useState<FileMeta[]>([]);
  const [audit, setAudit] = useState<AuditEvent[]>([]);
  const [name, setName] = useState("New TPRA Workspace");
  const [selectedFileIds, setSelectedFileIds] = useState<string[]>([]);
  const [agentId, setAgentId] = useState("uc1_structured_findings");
  const [log, setLog] = useState<string>("");
  const [busy, setBusy] = useState(false);

  const refresh = async (workspaceId?: string) => {
    const ws = await api.listWorkspaces(opts);
    setWorkspaces(ws);
    const ag = await api.listAgents(opts);
    setAgents(ag);
    const wid = workspaceId || selected || ws[0]?.id || "";
    if (wid) {
      setSelected(wid);
      setFiles(await api.listFiles(opts, wid));
      setAudit(await api.listAudit(opts, wid));
    }
  };

  useEffect(() => {
    refresh().catch((e) => setLog(String(e)));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [role]);

  const onCreate = async () => {
    setBusy(true);
    try {
      const ws = await api.createWorkspace(opts, { name, description: "Created from UI" });
      setLog(`Created workspace ${ws.id}`);
      await refresh(ws.id);
    } catch (e) {
      setLog(String(e));
    } finally {
      setBusy(false);
    }
  };

  const onUpload = async (fileList: FileList | null) => {
    if (!selected || !fileList?.length) return;
    setBusy(true);
    try {
      const uploaded = await api.uploadFile(opts, selected, fileList[0]);
      setLog(`Uploaded ${uploaded.filename}`);
      await refresh(selected);
    } catch (e) {
      setLog(String(e));
    } finally {
      setBusy(false);
    }
  };

  const toggleFile = (id: string) => {
    setSelectedFileIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
    );
  };

  const onRun = async () => {
    if (!selected) return;
    setBusy(true);
    try {
      const run = await api.runAgent(opts, selected, {
        agent_id: agentId,
        input_file_ids: selectedFileIds,
      });
      setLog(`Run ${run.id} → ${run.status}\n${JSON.stringify(run.result, null, 2)}`);
      await refresh(selected);
    } catch (e) {
      setLog(String(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div>
          <p className="brand">TPRA Agentic MVP</p>
          <h1>Third Party Risk Assessment Workspace</h1>
          <p className="sub">Run UC1 findings packaging and UC2 draft report generation with human review.</p>
        </div>
        <label className="role">
          Role
          <select value={role} onChange={(e) => setRole(e.target.value as Role)}>
            <option value="analyst">analyst</option>
            <option value="reviewer">reviewer</option>
            <option value="approver">approver</option>
            <option value="admin">admin</option>
          </select>
        </label>
      </header>

      <main className="grid">
        <section>
          <h2>Workspaces</h2>
          <div className="row">
            <input value={name} onChange={(e) => setName(e.target.value)} />
            <button disabled={busy} onClick={onCreate}>Create</button>
          </div>
          <ul className="list">
            {workspaces.map((w) => (
              <li key={w.id}>
                <button
                  className={selected === w.id ? "link active" : "link"}
                  onClick={() => refresh(w.id)}
                >
                  {w.name}
                </button>
              </li>
            ))}
          </ul>
        </section>

        <section>
          <h2>Files</h2>
          <input type="file" disabled={!selected || busy} onChange={(e) => onUpload(e.target.files)} />
          <ul className="list">
            {files.map((f) => (
              <li key={f.id}>
                <label>
                  <input
                    type="checkbox"
                    checked={selectedFileIds.includes(f.id)}
                    onChange={() => toggleFile(f.id)}
                  />
                  {f.filename} <span className="muted">({f.size} B)</span>
                </label>
              </li>
            ))}
          </ul>
        </section>

        <section>
          <h2>Agents</h2>
          <select value={agentId} onChange={(e) => setAgentId(e.target.value)}>
            {agents.map((a) => (
              <option key={a.id} value={a.id}>{a.name}</option>
            ))}
          </select>
          <p className="muted">{agents.find((a) => a.id === agentId)?.description}</p>
          <button disabled={!selected || busy || selectedFileIds.length === 0} onClick={onRun}>
            Run agent
          </button>
        </section>

        <section className="wide">
          <h2>Audit trail</h2>
          <ul className="list compact">
            {audit.map((e) => (
              <li key={e.id}>
                <strong>{e.action}</strong> by {e.actor}{" "}
                <span className="muted">{new Date(e.created_at).toLocaleString()}</span>
              </li>
            ))}
          </ul>
        </section>

        <section className="wide">
          <h2>Output</h2>
          <pre>{log || "Ready."}</pre>
        </section>
      </main>
    </div>
  );
}
