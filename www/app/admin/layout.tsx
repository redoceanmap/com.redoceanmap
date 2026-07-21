import type { Metadata } from "next";
import AdminGuard from "@/components/admin/AdminGuard";
import AdminShell from "@/components/admin/AdminShell";
import AdminToast from "@/components/admin/AdminToast";

export const metadata: Metadata = {
  title: "redoceanmap — 어드민",
  description: "서울 상권 분석 서비스 운영 콘솔",
};

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AdminGuard>
      <AdminShell>{children}</AdminShell>
      <AdminToast />
    </AdminGuard>
  );
}
