export interface JobResponse {
  job_id: string;
  status: "queued" | "started" | "finished" | "failed";
}

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function createJob(
  url: string,
  mode: string,
  limitQty: number
): Promise<JobResponse> {
  const response = await fetch(`${API_BASE_URL}/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, mode, limit_qty: limitQty })
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
