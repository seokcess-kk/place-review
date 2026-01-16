"use client";

import { useMutation } from "@tanstack/react-query";
import { useState } from "react";

import { createJob } from "@/lib/api";
import { useJobStatus } from "@/hooks/useJobStatus";
import { useScrapeStore } from "@/store/scrapeStore";

export default function HomePage() {
  const { url, mode, limitQty, limitDate, setUrl, setMode, setLimitQty, setLimitDate } =
    useScrapeStore();
  const [jobId, setJobId] = useState<string | null>(null);
  const { data: job, error: jobError } = useJobStatus(jobId);

  const mutation = useMutation({
    mutationFn: () => createJob({ url, mode, limitQty, limitDate }),
    onSuccess: (data) => setJobId(data.job_id)
  });

  const status = job?.status ?? (mutation.isPending ? "queued" : null);

  return (
    <main>
      <h1>Place Review Analyzer</h1>
      <p>리뷰 URL을 입력하고 수집/분석 작업을 실행하세요.</p>

      <form
        onSubmit={(event) => {
          event.preventDefault();
          mutation.mutate();
        }}
      >
        <div>
          <label htmlFor="url">네이버 플레이스 URL</label>
          <input
            id="url"
            type="url"
            value={url}
            onChange={(event) => setUrl(event.target.value)}
            placeholder="https://m.place.naver.com/place/"
            required
          />
        </div>

        <div>
          <label htmlFor="mode">수집 모드</label>
          <select
            id="mode"
            value={mode}
            onChange={(event) => setMode(event.target.value as "QTY" | "DATE")}
          >
            <option value="QTY">최근 N개 리뷰</option>
            <option value="DATE">특정 날짜 이후</option>
          </select>
        </div>

        <div>
          <label htmlFor="limitQty">수집 개수 (QTY 모드)</label>
          <input
            id="limitQty"
            type="number"
            min={1}
            value={limitQty}
            onChange={(event) => setLimitQty(Number(event.target.value))}
            disabled={mode !== "QTY"}
          />
        </div>

        <div>
          <label htmlFor="limitDate">기준 날짜 (DATE 모드)</label>
          <input
            id="limitDate"
            type="date"
            value={limitDate}
            onChange={(event) => setLimitDate(event.target.value)}
            disabled={mode !== "DATE"}
          />
        </div>

        <button type="submit" disabled={mutation.isPending}>
          {mutation.isPending ? "작업 생성 중..." : "작업 시작"}
        </button>
      </form>

      <section>
        <div className="status">
          <span className="badge">Job Status</span>
          <strong>{status ?? "idle"}</strong>
        </div>
        {jobId && <p>Job ID: {jobId}</p>}
        {mutation.error ? (
          <p className="error">{(mutation.error as Error).message}</p>
        ) : null}
        {jobError ? <p className="error">{(jobError as Error).message}</p> : null}
        {job?.result ? (
          <p>
            완료: {job.result.review_count}건 수집, {job.result.analyzed_count}건 분석
          </p>
        ) : null}
      </section>
    </main>
  );
}
