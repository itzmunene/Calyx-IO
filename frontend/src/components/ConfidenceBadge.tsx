import { cn } from "@/lib/utils";

interface ConfidenceBadgeProps {
  confidence: number;
  className?: string;
}

export function ConfidenceBadge({ confidence, className }: ConfidenceBadgeProps) {
  const percentage = Math.round(confidence * 100);
  
  const getConfidenceLevel = () => {
    if (confidence >= 0.7) return "high";
    if (confidence >= 0.4) return "medium";
    return "low";
  };

  const level = getConfidenceLevel();

  return (
    <span
      className={cn(
        "inline-flex items-center px-3 py-1 rounded-full text-sm font-medium",
        level === "high" && "confidence-high",
        level === "medium" && "confidence-medium",
        level === "low" && "confidence-low",
        className
      )}
    >
      {percentage}% match
    </span>
  );
}