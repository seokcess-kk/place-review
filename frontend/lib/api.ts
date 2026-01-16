export interface JobResponse {
  job_id: string;
  status: "queued" | "started" | "finished" | "failed";
  result?: {
    review_count: number;
    analyzed_count: number;
  };
}

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

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
