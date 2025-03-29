// components/core/RoadmapTree.tsx
"use client";
import { RoadmapNode } from "@/components/core/RoadmapNode";
// CORRECTED IMPORT PATH: Import types from the types directory
import type { RoadmapStep } from "@/components/types/roadmap";

interface RoadmapTreeProps {
  data: RoadmapStep[];
}

export function RoadmapTree({ data }: RoadmapTreeProps) {
  if (!data || data.length === 0) {
    return (
      <p className="text-muted-foreground">No roadmap steps defined yet.</p>
    );
  }

  return (
    <div className="space-y-2">
      {data.map((node) => (
        <RoadmapNode key={node.id} node={node} level={0} />
      ))}
    </div>
  );
}
