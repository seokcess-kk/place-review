import { create } from "zustand";

type ScrapeMode = "QTY" | "DATE" | "DATE_RANGE";

interface ScrapeState {
  placeId: string;
  mode: ScrapeMode;
  limitQty: number;
  startDate: string;
  endDate: string;
  setPlaceId: (placeId: string) => void;
  setMode: (mode: ScrapeMode) => void;
  setLimitQty: (limit: number) => void;
  setStartDate: (date: string) => void;
  setEndDate: (date: string) => void;
}

export const useScrapeStore = create<ScrapeState>((set) => ({
  placeId: "1414590796",
  mode: "QTY",
  limitQty: 10,
  startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
  endDate: new Date().toISOString().slice(0, 10),
  setPlaceId: (placeId) => set({ placeId }),
  setMode: (mode) => set({ mode }),
  setLimitQty: (limitQty) => set({ limitQty }),
  setStartDate: (startDate) => set({ startDate }),
  setEndDate: (endDate) => set({ endDate })
}));
