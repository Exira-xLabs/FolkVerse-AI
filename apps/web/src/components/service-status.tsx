"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { api, type Health, type AnonymousSession } from "@folkverse/contracts";
import { useLocale } from "./locale-provider";

async function requestHealth(signal: AbortSignal): Promise<Health | null> {
  try {
    const { data, error } = await api.GET("/api/v1/health", { signal });
    const result = data ?? error;
    return result && "status" in result ? result : null;
  } catch { return null; }
}

export function ServiceStatus() {
  const { t, locale } = useLocale();
  const [health, setHealth] = useState<Health | null>(null);
  const [loading, setLoading] = useState(true);
  const [failed, setFailed] = useState(false);
  const [checkedAt, setCheckedAt] = useState<Date | null>(null);
  const [session, setSession] = useState<AnonymousSession | null>(null);
  const [sessionBusy, setSessionBusy] = useState(false);
  const [sessionFailed, setSessionFailed] = useState(false);

  const applyHealth = useCallback((result: Health | null) => {
    setHealth(result);
    setFailed(result === null);
    setLoading(false);
    setCheckedAt(new Date());
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    const signal = AbortSignal.any([controller.signal, AbortSignal.timeout(7000)]);
    void requestHealth(signal).then(result => {
      if (!controller.signal.aborted) applyHealth(result);
    });
    void api.GET("/api/v1/session", { signal })
      .then(({ data }) => { if (data && !controller.signal.aborted) setSession(data); }).catch(() => {});
    return () => controller.abort();
  }, [applyHealth]);

  async function changeSession() {
    setSessionBusy(true);
    setSessionFailed(false);
    try {
      if (session) {
        const { error } = await api.DELETE("/api/v1/session", { signal: AbortSignal.timeout(7000) });
        if (error) throw new Error("Delete failed");
        setSession(null);
      } else {
        const { data } = await api.POST("/api/v1/session", { signal: AbortSignal.timeout(7000) });
        if (!data) throw new Error("Start failed");
        setSession(data);
      }
    } catch { setSessionFailed(true); }
    finally { setSessionBusy(false); }
  }

  const statusLabel = loading ? t.status.checking : failed ? t.status.error
    : health?.status === "ok" ? t.status.ok : t.status.degraded;
  const available = (value: string | undefined) => value === "available" ? t.status.available
    : value === "current" ? t.status.current : t.status.unavailable;

  return <div className="status-panels">
    <section className="glass-panel status-panel" aria-labelledby="connection-title" aria-busy={loading}>
      <h2 id="connection-title" className="service-heading">{t.nav.status}</h2>
      <p role="status" className={health?.status === "ok" ? "connection-ok" : "connection-message"}>{statusLabel}</p>
      <p>{t.status.description}</p>
      {checkedAt && <p className="fine-print">{t.status.lastChecked} <time dateTime={checkedAt.toISOString()}>{checkedAt.toLocaleTimeString(locale)}</time></p>}
      <div className="status-actions"><button className="gold-button" disabled={loading} onClick={() => {
        setLoading(true);
        setFailed(false);
        void requestHealth(AbortSignal.timeout(7000)).then(applyHealth);
      }}>{t.status.refresh}</button><Link className="outline-button" href="/explore">{locale === "en" ? "Explore the collection" : "探索馆藏"} ↗︎</Link></div>
      <details className="service-diagnostics"><summary>{t.status.diagnostics}</summary><dl className="service-list">
        {[
          [t.status.database, available(health?.database)],
          [t.status.vector, available(health?.pgvector)],
          [t.status.schema, available(health?.schema_status)],
          [t.status.mode, health?.mode ?? "—"],
        ].map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{loading ? "—" : value}</dd></div>)}
      </dl></details>
    </section>
    <section className="glass-panel status-panel" aria-labelledby="visit-title">
      <h2 id="visit-title" className="service-heading">{t.status.session}</h2>
      <p>{t.status.privacy}</p>
      {session && <p role="status" className="connection-ok">{t.status.anonymous}</p>}
      {sessionFailed && <p role="alert">{t.status.sessionError}</p>}
      <button className="outline-button" onClick={() => void changeSession()} disabled={sessionBusy}>
        {session ? t.status.clear : t.status.start}
      </button>
    </section>
  </div>;
}
