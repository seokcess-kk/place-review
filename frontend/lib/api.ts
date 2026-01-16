export interface AspectData {
  aspect: string;
  sentiment: "Positive" | "Negative" | "Neutral";
}

export interface ReviewData {
  id: number;
  text: string;
  date: string;
  sentiment: "Positive" | "Negative" | "Neutral" | null;
  aspects: AspectData[];
  keywords: string[];
  summary: string | null;
}

export interface JobResult {
  place_id: number | null;
  place_url: string | null;
  review_count: number;
  analyzed_count: number;
  reviews: ReviewData[];
}

export interface JobProgress {
  current: number;
  total: number;
  stage: string;
  percent: number;
}

export interface JobResponse {
  job_id: string;
  status: "queued" | "started" | "finished" | "failed";
  progress?: JobProgress;
  result?: JobResult;
  error?: string;
}

const API_BASE_URL = "/api";

interface CreateJobPayload {
  url: string;
  mode: "QTY" | "DATE";
  limitQty: number;
  limitDate: string;
}

export async function createJob({
  url,
  mode,
  limitQty,
  limitDate
}: CreateJobPayload): Promise<JobResponse> {
  const payload: Record<string, string | number> = { url, mode };
  if (mode === "QTY") {
    payload.limit_qty = limitQty;
  } else {
    payload.limit_date = limitDate;
  }

  const response = await fetch(`${API_BASE_URL}/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const payload = await response.json();
    throw new Error(payload.detail ?? "Failed to create job");
  }

  return response.json();
}

export async function fetchJob(jobId: string): Promise<JobResponse> {
  const response = await fetch(`${API_BASE_URL}/jobs/${jobId}`);

  if (!response.ok) {
    const payload = await response.json();
    throw new Error(payload.detail ?? "Failed to fetch job");
  }

  return response.json();
}
