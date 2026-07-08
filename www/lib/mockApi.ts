export type AreaStats = {
  // 수익성 (공공데이터 실계산)
  monthlyRevenueText: string;
  revenueSourceText: string;
  weekdayText: string;
  // 점포 현황
  storeCountText: string;
  closureRateText: string;
  openingRateText: string;
  franchiseText: string;
  // 유동인구
  footTrafficText: string;
  topAgeText: string;
  peakTimeText: string;
  // 상권 변화
  changeText: string;
  operatingMonthsText: string;
  // 메타
  dataSource: string;
  hasRealData: boolean;
};

export type Area = {
  id: string;
  name: string;
  lat: number;
  lng: number;
  category: string;
  reason: string;
  stats: AreaStats;
};
