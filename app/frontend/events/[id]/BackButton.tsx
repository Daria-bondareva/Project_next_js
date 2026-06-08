"use client";

import { useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import Button from "@/components/ui/Button";

export default function BackButton() {
  const router = useRouter();

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={() => router.back()}
      aria-label="Повернутися назад"
    >
      <ArrowLeft size={16} />
      Назад
    </Button>
  );
}
