import { create } from 'zustand';

export interface FilterState {
  industry: string;
  region: string;
  minDuration: number | undefined;
  sort: string;
  page: number;
}

interface FilterActions {
  setIndustry: (industry: string) => void;
  setRegion: (region: string) => void;
  setMinDuration: (duration: number | undefined) => void;
  setSort: (sort: string) => void;
  setPage: (page: number) => void;
  resetFilters: () => void;
}

const initialState: FilterState = {
  industry: '',
  region: '',
  minDuration: undefined,
  sort: '-collected_at',
  page: 1,
};

export const useFilterStore = create<FilterState & FilterActions>((set) => ({
  ...initialState,

  setIndustry: (industry) => set({ industry, page: 1 }),
  setRegion: (region) => set({ region, page: 1 }),
  setMinDuration: (minDuration) => set({ minDuration, page: 1 }),
  setSort: (sort) => set({ sort, page: 1 }),
  setPage: (page) => set({ page }),
  resetFilters: () => set(initialState),
}));
