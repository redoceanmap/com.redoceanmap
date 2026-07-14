"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { AreaStatsDetail } from "@/lib/types";

const formatPop = (v: number) => {
  if (Math.abs(v) >= 1e4) return `${(v / 1e4).toFixed(0)}만`;
  return v.toLocaleString("ko-KR");
};

function PopBarChart({ data }: { data: { label: string; value: number }[] }) {
  return (
    <div className="h-32">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 4, right: 4, bottom: 0, left: 0 }}>
          <CartesianGrid stroke="#EBE8DF" strokeDasharray="3 3" vertical={false} />
          <XAxis
            dataKey="label"
            tick={{ fontSize: 10, fill: "#6B7280" }}
            axisLine={{ stroke: "#EBE8DF" }}
            tickLine={false}
          />
          <YAxis
            tickFormatter={formatPop}
            tick={{ fontSize: 10, fill: "#6B7280" }}
            axisLine={false}
            tickLine={false}
            width={36}
          />
          <Tooltip
            formatter={(v) => [`${Number(v).toLocaleString("ko-KR")}명`, "유동인구"]}
            contentStyle={{ fontSize: 12, borderRadius: 8, border: "1px solid #EBE8DF" }}
            cursor={{ fill: "rgba(153, 27, 27, 0.06)" }}
          />
          <Bar dataKey="value" fill="#991B1B" radius={[3, 3, 0, 0]} maxBarSize={28} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default function PopulationCharts({ latest }: { latest: AreaStatsDetail["latest"] }) {
  const { floatingByAge: age, floatingByTime: time } = latest;
  if (!age && !time) {
    return <p className="text-sm text-foreground-muted">유동인구 데이터가 없습니다.</p>;
  }

  return (
    <div className="flex flex-col gap-4">
      {age && (
        <div>
          <p className="text-xs text-foreground-muted mb-1.5">연령대별</p>
          <PopBarChart
            data={[
              { label: "10대", value: age.age10 },
              { label: "20대", value: age.age20 },
              { label: "30대", value: age.age30 },
              { label: "40대", value: age.age40 },
              { label: "50대", value: age.age50 },
              { label: "60+", value: age.age60Plus },
            ]}
          />
        </div>
      )}
      {time && (
        <div>
          <p className="text-xs text-foreground-muted mb-1.5">시간대별</p>
          <PopBarChart
            data={[
              { label: "0-6시", value: time.t00_06 },
              { label: "6-11시", value: time.t06_11 },
              { label: "11-14시", value: time.t11_14 },
              { label: "14-17시", value: time.t14_17 },
              { label: "17-21시", value: time.t17_21 },
              { label: "21-24시", value: time.t21_24 },
            ]}
          />
        </div>
      )}
    </div>
  );
}
