// components/core/RoadmapNode.tsx
"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
// CORRECTED IMPORT PATH: Import types from the types directory
import type {
  RoadmapStep,
  RoadmapStepType,
  RoadmapStepStatus,
} from "@/components/types/roadmap";
import {
  ChevronRight,
  BookOpen,
  Folder,
  CheckSquare,
  HelpCircle,
  Link as LinkIcon,
  Lock,
  CircleDot,
  Check,
  XCircle,
  Minus,
  FileText,
} from "lucide-react";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";

const getTypeIcon = (type: RoadmapStepType): React.ReactElement => {
  const Icon =
    {
      lesson: BookOpen,
      module: Folder,
      quiz: CheckSquare,
      assignment: CheckSquare,
      section: FileText,
      external_resource: LinkIcon,
    }[type] || HelpCircle;

  return <Icon className="h-4 w-4 mr-2 flex-shrink-0" aria-hidden="true" />;
};

const getStatusInfo = (
  status: RoadmapStepStatus
): { icon: React.ReactElement; className: string } => {
  switch (status) {
    case "locked":
      return {
        icon: <Lock className="h-4 w-4 ml-2 flex-shrink-0" />,
        className: "text-muted-foreground opacity-60",
      };
    case "unlocked":
      return {
        icon: (
          <CircleDot className="h-4 w-4 ml-2 flex-shrink-0 text-blue-500" />
        ),
        className: "text-foreground",
      };
    case "inprogress":
      return {
        icon: (
          <CircleDot className="h-4 w-4 ml-2 flex-shrink-0 text-yellow-500 animate-pulse" />
        ),
        className: "text-foreground font-medium",
      };
    case "completed":
      return {
        icon: <Check className="h-4 w-4 ml-2 flex-shrink-0 text-green-600" />,
        className: "text-muted-foreground line-through",
      };
    case "failed":
      return {
        icon: (
          <XCircle className="h-4 w-4 ml-2 flex-shrink-0 text-destructive" />
        ),
        className: "text-destructive",
      };
    default:
      return {
        icon: <Minus className="h-4 w-4 ml-2 flex-shrink-0" />,
        className: "text-muted-foreground",
      };
  }
};

interface RoadmapNodeProps {
  node: RoadmapStep;
  level: number;
}

export function RoadmapNode({ node, level }: RoadmapNodeProps) {
  const hasChildren = node.children && node.children.length > 0;
  const isLocked = node.status === "locked";
  const statusInfo = getStatusInfo(node.status);
  const isCollapsible =
    hasChildren && (node.type === "module" || node.type === "section");
  const indentationStyle = { paddingLeft: `${level * 1.5}rem` };

  const NodeContent = (
    <div
      className={cn(
        "flex items-center justify-between w-full py-1.5 px-2 rounded transition-colors duration-150 group",
        isLocked ? "cursor-not-allowed" : "cursor-pointer hover:bg-muted/50",
        statusInfo.className
      )}
      style={indentationStyle}
    >
      <div className="flex items-center overflow-hidden mr-2">
        {getTypeIcon(node.type)}
        <span className="truncate font-medium text-sm">{node.title}</span>
      </div>
      <div className="flex items-center flex-shrink-0">
        {statusInfo.icon}
        {isCollapsible && (
          <ChevronRight className="h-4 w-4 ml-1 text-muted-foreground transition-transform duration-200 group-data-[state=open]:rotate-90" />
        )}
      </div>
    </div>
  );

  if (isCollapsible) {
    return (
      <Collapsible defaultOpen={level < 1}>
        <CollapsibleTrigger
          asChild
          className={cn(isLocked ? "cursor-not-allowed" : "")}
        >
          {NodeContent}
        </CollapsibleTrigger>
        <CollapsibleContent className="overflow-hidden data-[state=closed]:animate-collapsible-up data-[state=open]:animate-collapsible-down">
          <div className="mt-1 space-y-1">
            {node.children.map((childNode) => (
              <RoadmapNode
                key={childNode.id}
                node={childNode}
                level={level + 1}
              />
            ))}
          </div>
        </CollapsibleContent>
      </Collapsible>
    );
  } else {
    return (
      <div>
        {NodeContent}
        {hasChildren && (
          <div className="mt-1 space-y-1">
            {node.children.map((childNode) => (
              <RoadmapNode
                key={childNode.id}
                node={childNode}
                level={level + 1}
              />
            ))}
          </div>
        )}
      </div>
    );
  }
}
