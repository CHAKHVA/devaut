// components/core/BadgeDisplay.tsx
// Removed Avatar imports
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Award } from "lucide-react"; // Fallback icon

import type { BadgeData } from "@/components/types/badge"; // Make sure path is correct

interface BadgeDisplayProps {
  badge: BadgeData;
  showDetails?: boolean; // Optionally show name/date below
}

export function BadgeDisplay({
  badge,
  showDetails = false,
}: BadgeDisplayProps) {
  // Determine fallback content (initial or icon)
  const fallbackContent = badge.name ? (
    badge.name.substring(0, 1).toUpperCase()
  ) : (
    <Award className="h-8 w-8" /> // Made icon slightly larger for visibility
  );

  return (
    <TooltipProvider delayDuration={100}>
      <Tooltip>
        <TooltipTrigger asChild>
          <div className="flex flex-col items-center text-center gap-1 cursor-default">
            {/* Conditional rendering: Use img if iconUrl exists, otherwise use fallback div */}
            {badge.iconUrl ? (
              <img
                src={badge.iconUrl}
                alt={badge.name}
                className="h-16 w-16 border-2 border-amber-400 dark:border-amber-500 rounded-full object-cover" // Added rounded-full and object-cover for similar appearance
              />
            ) : (
              // Fallback container mimicking Avatar appearance
              <div className="h-16 w-16 border-2 border-amber-400 dark:border-amber-500 rounded-full flex items-center justify-center bg-muted text-muted-foreground text-xl font-semibold">
                {fallbackContent}
              </div>
            )}

            {/* Details section remains the same */}
            {showDetails && (
              <>
                <p className="text-xs font-semibold mt-1 line-clamp-1">
                  {badge.name}
                </p>
                {badge.earnedDate && (
                  <p className="text-xs text-muted-foreground">
                    {new Date(badge.earnedDate).toLocaleDateString()}
                  </p>
                )}
              </>
            )}
          </div>
        </TooltipTrigger>
        {/* Tooltip content remains the same */}
        <TooltipContent side="bottom" className="max-w-[200px] text-center">
          <p className="font-semibold mb-1">{badge.name}</p>
          <p className="text-xs text-muted-foreground">{badge.description}</p>
          {badge.earnedDate && (
            <p className="text-xs text-muted-foreground mt-1">
              Earned: {new Date(badge.earnedDate).toLocaleDateString()}
            </p>
          )}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
