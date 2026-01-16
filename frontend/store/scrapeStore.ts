import { create } from "zustand";

type ScrapeMode = "QTY" | "DATE";

interface ScrapeState {
  url: string;
  mode: ScrapeMode;
  limitQty: number;
  limitDate: string;
  setUrl: (url: string) => void;
  setMode: (mode: ScrapeMode) => void;
  setLimitQty: (limit: number) => void;
  setLimitDate: (date: string) => void;
}

export const useScrapeStore = create<ScrapeState>((set) => ({
  url: "https://m.place.naver.com/place/1414590796",
  mode: "QTY",
  limitQty: 10,
  limitDate: new Date().toISOString().slice(0, 10),
  setUrl: (url) => set({ url }),
  setMode: (mode) => set({ mode }),
  setLimitQty: (limitQty) => set({ limitQty }),
  setLimitDate: (limitDate) => set({ limitDate })
}));
