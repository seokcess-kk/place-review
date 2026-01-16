import { useQuery } from "@tanstack/react-query";

import { fetchJob } from "@/lib/api";

export function useJobStatus(jobId: string | null) {
  return useQuery({
    queryKey: ["job", jobId],
    queryFn: () => fetchJob(jobId ?? ""),
    enabled: Boolean(jobId),
    refetchInterval: (query) =>
      query.state.data?.status === "finished" || query.state.data?.status === "failed"
        ? false
        : 3000
  });
}
