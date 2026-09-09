import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

const toneText: Record<string, string> = {
  default: "text-foreground",
  danger: "text-destructive",
  warning: "text-amber-600 dark:text-amber-500",
  success: "text-emerald-600 dark:text-emerald-500",
};

const toneChip: Record<string, string> = {
  default: "bg-primary/10 text-primary",
  danger: "bg-destructive/10 text-destructive",
  warning: "bg-amber-500/10 text-amber-600 dark:text-amber-500",
  success: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-500",
};

export function StatCard({
  label,
  value,
  icon,
  tone = "default",
}: {
  label: string;
  value: React.ReactNode;
  icon?: React.ReactNode;
  tone?: "default" | "danger" | "warning" | "success";
}) {
  return (
    <Card className="transition-shadow hover:shadow-md">
      <CardContent className="flex items-center justify-between">
        <div>
          <p className="text-xs font-medium tracking-wide text-muted-foreground uppercase">{label}</p>
          <p className={cn("mt-1 text-2xl font-semibold tabular-nums", toneText[tone])}>{value}</p>
        </div>
        {icon && (
          <div className={cn("flex h-11 w-11 shrink-0 items-center justify-center rounded-xl", toneChip[tone])}>
            {icon}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
