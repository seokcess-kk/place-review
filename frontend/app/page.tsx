"use client";

import { useMutation } from "@tanstack/react-query";
import { useState, useEffect } from "react";

import { createJob, JobProgress, ReviewData, AspectData } from "@/lib/api";
import { useJobStatus } from "@/hooks/useJobStatus";
import { useScrapeStore } from "@/store/scrapeStore";

function ProgressBar({ progress }: { progress: JobProgress | undefined }) {
  if (!progress) return null;

  const stageText =
    progress.stage === "scraping"
      ? "리뷰 수집 중..."
      : progress.stage === "analyzing"
        ? `분석 중 (${progress.current}/${progress.total})`
        : "처리 중...";

  return (
    <div className="progress-container">
      <div className="progress-info">
        <span>{stageText}</span>
        <span>{progress.percent}%</span>
      </div>
      <div className="progress-track">
        <div
          className="progress-fill"
          style={{ width: `${progress.percent}%` }}
        />
      </div>
    </div>
  );
}

function Toast({
  message,
  type,
  onClose,
}: {
  message: string;
  type: "success" | "error";
  onClose: () => void;
}) {
  useEffect(() => {
    const timer = setTimeout(onClose, 5000);
    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className={`toast toast-${type}`}>
      <span>{message}</span>
      <button onClick={onClose} className="toast-close">
        ×
      </button>
    </div>
  );
}

function StatusBadge({ status }: { status: string | null }) {
  const getStatusColor = () => {
    switch (status) {
      case "queued":
        return "badge-queued";
      case "started":
        return "badge-started";
      case "finished":
        return "badge-finished";
      case "failed":
        return "badge-failed";
      default:
        return "badge-idle";
    }
  };

  const getStatusText = () => {
    switch (status) {
      case "queued":
        return "대기중";
      case "started":
        return "처리중";
      case "finished":
        return "완료";
      case "failed":
        return "실패";
      default:
        return "대기";
    }
  };

  return (
    <span className={`status-badge ${getStatusColor()}`}>
      {status === "started" && <span className="spinner" />}
      {getStatusText()}
    </span>
  );
}

function SentimentBadge({ sentiment }: { sentiment: string | null }) {
  const getClass = () => {
    switch (sentiment) {
      case "Positive":
        return "sentiment-positive";
      case "Negative":
        return "sentiment-negative";
      case "Neutral":
        return "sentiment-neutral";
      default:
        return "sentiment-unknown";
    }
  };

  const getText = () => {
    switch (sentiment) {
      case "Positive":
        return "긍정";
      case "Negative":
        return "부정";
      case "Neutral":
        return "중립";
      default:
        return "-";
    }
  };

  return <span className={`sentiment-badge ${getClass()}`}>{getText()}</span>;
}

function StatsCard({
  label,
  value,
  color,
}: {
  label: string;
  value: number;
  color: string;
}) {
  return (
    <div className={`stats-card ${color}`}>
      <div className="stats-value">{value}</div>
      <div className="stats-label">{label}</div>
    </div>
  );
}

function SentimentChart({ reviews }: { reviews: ReviewData[] }) {
  const positive = reviews.filter((r) => r.sentiment === "Positive").length;
  const negative = reviews.filter((r) => r.sentiment === "Negative").length;
  const neutral = reviews.filter((r) => r.sentiment === "Neutral").length;
  const total = reviews.length || 1;

  return (
    <div className="sentiment-chart">
      <h3>감성 분석 결과</h3>
      <div className="chart-bars">
        <div className="chart-bar">
          <div className="bar-label">긍정</div>
          <div className="bar-track">
            <div
              className="bar-fill positive"
              style={{ width: `${(positive / total) * 100}%` }}
            />
          </div>
          <div className="bar-value">
            {positive}건 ({Math.round((positive / total) * 100)}%)
          </div>
        </div>
        <div className="chart-bar">
          <div className="bar-label">중립</div>
          <div className="bar-track">
            <div
              className="bar-fill neutral"
              style={{ width: `${(neutral / total) * 100}%` }}
            />
          </div>
          <div className="bar-value">
            {neutral}건 ({Math.round((neutral / total) * 100)}%)
          </div>
        </div>
        <div className="chart-bar">
          <div className="bar-label">부정</div>
          <div className="bar-track">
            <div
              className="bar-fill negative"
              style={{ width: `${(negative / total) * 100}%` }}
            />
          </div>
          <div className="bar-value">
            {negative}건 ({Math.round((negative / total) * 100)}%)
          </div>
        </div>
      </div>
    </div>
  );
}

function KeywordCloud({ reviews }: { reviews: ReviewData[] }) {
  const keywordCounts: Record<string, number> = {};
  reviews.forEach((r) => {
    r.keywords.forEach((k) => {
      keywordCounts[k] = (keywordCounts[k] || 0) + 1;
    });
  });

  const sortedKeywords = Object.entries(keywordCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 15);

  if (sortedKeywords.length === 0) return null;

  return (
    <div className="keyword-cloud">
      <h3>주요 키워드</h3>
      <div className="keywords">
        {sortedKeywords.map(([keyword, count]) => (
          <span key={keyword} className="keyword-tag">
            {keyword} <span className="keyword-count">{count}</span>
          </span>
        ))}
      </div>
    </div>
  );
}

function AspectChart({ reviews }: { reviews: ReviewData[] }) {
  const aspectStats: Record<
    string,
    { positive: number; negative: number; neutral: number }
  > = {};

  reviews.forEach((r) => {
    (r.aspects || []).forEach((asp: AspectData) => {
      if (!aspectStats[asp.aspect]) {
        aspectStats[asp.aspect] = { positive: 0, negative: 0, neutral: 0 };
      }
      if (asp.sentiment === "Positive") aspectStats[asp.aspect].positive++;
      else if (asp.sentiment === "Negative") aspectStats[asp.aspect].negative++;
      else aspectStats[asp.aspect].neutral++;
    });
  });

  const sortedAspects = Object.entries(aspectStats)
    .map(([aspect, counts]) => ({
      aspect,
      ...counts,
      total: counts.positive + counts.negative + counts.neutral,
    }))
    .sort((a, b) => b.total - a.total)
    .slice(0, 8);

  if (sortedAspects.length === 0) return null;

  return (
    <div className="aspect-chart">
      <h3>속성별 감성 분석</h3>
      <div className="aspect-bars">
        {sortedAspects.map(({ aspect, positive, negative, neutral, total }) => (
          <div key={aspect} className="aspect-row">
            <div className="aspect-label">{aspect}</div>
            <div className="aspect-bar-container">
              <div className="aspect-bar">
                {positive > 0 && (
                  <div
                    className="aspect-segment positive"
                    style={{ width: `${(positive / total) * 100}%` }}
                    title={`긍정: ${positive}건`}
                  />
                )}
                {neutral > 0 && (
                  <div
                    className="aspect-segment neutral"
                    style={{ width: `${(neutral / total) * 100}%` }}
                    title={`중립: ${neutral}건`}
                  />
                )}
                {negative > 0 && (
                  <div
                    className="aspect-segment negative"
                    style={{ width: `${(negative / total) * 100}%` }}
                    title={`부정: ${negative}건`}
                  />
                )}
              </div>
              <span className="aspect-count">{total}건</span>
            </div>
          </div>
        ))}
      </div>
      <div className="aspect-legend">
        <span className="legend-item">
          <span className="legend-dot positive"></span>긍정
        </span>
        <span className="legend-item">
          <span className="legend-dot neutral"></span>중립
        </span>
        <span className="legend-item">
          <span className="legend-dot negative"></span>부정
        </span>
      </div>
    </div>
  );
}

function ReviewTable({ reviews }: { reviews: ReviewData[] }) {
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;
  const totalPages = Math.ceil(reviews.length / pageSize);
  const paginatedReviews = reviews.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize,
  );

  return (
    <div className="review-table-container">
      <h3>수집된 리뷰 ({reviews.length}건)</h3>
      <div className="review-table">
        <div className="table-header">
          <div className="col-date">날짜</div>
          <div className="col-sentiment">감성</div>
          <div className="col-text">리뷰 내용</div>
          <div className="col-keywords">키워드</div>
        </div>
        {paginatedReviews.map((review) => (
          <div key={review.id} className="table-row">
            <div className="col-date">{review.date}</div>
            <div className="col-sentiment">
              <SentimentBadge sentiment={review.sentiment} />
            </div>
            <div className="col-text">
              <div className="review-text">{review.text}</div>
              {review.summary && (
                <div className="review-summary">{review.summary}</div>
              )}
            </div>
            <div className="col-keywords">
              {review.keywords.map((k, i) => (
                <span key={i} className="keyword-mini">
                  {k}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
      {totalPages > 1 && (
        <div className="pagination">
          <button
            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            disabled={currentPage === 1}
          >
            이전
          </button>
          <span>
            {currentPage} / {totalPages}
          </span>
          <button
            onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
            disabled={currentPage === totalPages}
          >
            다음
          </button>
        </div>
      )}
    </div>
  );
}

export default function HomePage() {
  const {
    url,
    mode,
    limitQty,
    limitDate,
    setUrl,
    setMode,
    setLimitQty,
    setLimitDate,
  } = useScrapeStore();
  const [jobId, setJobId] = useState<string | null>(null);
  const [toast, setToast] = useState<{
    message: string;
    type: "success" | "error";
  } | null>(null);
  const [prevStatus, setPrevStatus] = useState<string | null>(null);
  const { data: job, error: jobError } = useJobStatus(jobId);

  const mutation = useMutation({
    mutationFn: () => createJob({ url, mode, limitQty, limitDate }),
    onSuccess: (data) => setJobId(data.job_id),
    onError: (error) =>
      setToast({ message: (error as Error).message, type: "error" }),
  });

  const status = job?.status ?? (mutation.isPending ? "queued" : null);
  const isProcessing = status === "queued" || status === "started";

  useEffect(() => {
    if (prevStatus !== status) {
      if (status === "finished" && prevStatus === "started") {
        setToast({ message: "분석이 완료되었습니다!", type: "success" });
      } else if (status === "failed" && prevStatus === "started") {
        setToast({ message: "작업 중 오류가 발생했습니다", type: "error" });
      }
      setPrevStatus(status);
    }
  }, [status, prevStatus]);

  return (
    <main>
      <header className="page-header">
        <h1>Review Analyzer</h1>
        <p>네이버 플레이스 리뷰를 수집하고 AI로 분석합니다</p>
      </header>

      <form
        onSubmit={(event) => {
          event.preventDefault();
          mutation.mutate();
        }}
      >
        <div className="form-group">
          <label htmlFor="url">네이버 플레이스 URL</label>
          <input
            id="url"
            type="url"
            value={url}
            onChange={(event) => setUrl(event.target.value)}
            placeholder="https://m.place.naver.com/place/..."
            required
            disabled={isProcessing}
          />
          <span className="input-hint">
            모바일 네이버 플레이스 URL을 입력하세요
          </span>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="mode">수집 모드</label>
            <select
              id="mode"
              value={mode}
              onChange={(event) =>
                setMode(event.target.value as "QTY" | "DATE")
              }
              disabled={isProcessing}
            >
              <option value="QTY">최근 N개 리뷰</option>
              <option value="DATE">특정 날짜 이후</option>
            </select>
          </div>

          {mode === "QTY" ? (
            <div className="form-group">
              <label htmlFor="limitQty">수집 개수</label>
              <input
                id="limitQty"
                type="number"
                min={1}
                max={100}
                value={limitQty}
                onChange={(event) => setLimitQty(Number(event.target.value))}
                disabled={isProcessing}
              />
            </div>
          ) : (
            <div className="form-group">
              <label htmlFor="limitDate">기준 날짜</label>
              <input
                id="limitDate"
                type="date"
                value={limitDate}
                onChange={(event) => setLimitDate(event.target.value)}
                disabled={isProcessing}
              />
            </div>
          )}
        </div>

        <button type="submit" disabled={mutation.isPending || isProcessing}>
          {isProcessing ? (
            <>
              <span className="spinner" />
              처리 중...
            </>
          ) : (
            "분석 시작"
          )}
        </button>
      </form>

      <section className="status-section">
        <div className="status-header">
          <StatusBadge status={status} />
          {jobId && <span className="job-id">Job: {jobId.slice(0, 8)}...</span>}
        </div>

        {isProcessing && <ProgressBar progress={job?.progress} />}

        {mutation.error && (
          <div className="error-message">
            {(mutation.error as Error).message}
          </div>
        )}
        {jobError && (
          <div className="error-message">{(jobError as Error).message}</div>
        )}
        {job?.error && (
          <div className="error-message">작업 실패: {job.error}</div>
        )}
      </section>

      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}

      {job?.result && (
        <section className="results-section">
          <div className="stats-grid">
            <StatsCard
              label="수집된 리뷰"
              value={job.result.review_count}
              color="blue"
            />
            <StatsCard
              label="분석 완료"
              value={job.result.analyzed_count}
              color="green"
            />
            <StatsCard
              label="긍정 리뷰"
              value={
                job.result.reviews.filter((r) => r.sentiment === "Positive")
                  .length
              }
              color="positive"
            />
            <StatsCard
              label="부정 리뷰"
              value={
                job.result.reviews.filter((r) => r.sentiment === "Negative")
                  .length
              }
              color="negative"
            />
          </div>

          <div className="analysis-grid">
            <SentimentChart reviews={job.result.reviews} />
            <KeywordCloud reviews={job.result.reviews} />
            <AspectChart reviews={job.result.reviews} />
          </div>

          <ReviewTable reviews={job.result.reviews} />
        </section>
      )}
    </main>
  );
}
