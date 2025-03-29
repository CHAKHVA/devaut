export type RoadmapStepType =
  | "lesson"
  | "module"
  | "quiz"
  | "assignment"
  | "section"
  | "external_resource";

export type RoadmapStepStatus =
  | "locked"
  | "unlocked"
  | "inprogress"
  | "completed"
  | "failed";

export interface RoadmapStep {
  id: string;
  title: string;
  type: RoadmapStepType;
  status: RoadmapStepStatus;
  description?: string | null;
  estimatedDuration?: string | null;
  children: RoadmapStep[];
}

export interface Roadmap {
  id: string;
  title: string;
  description: string;
  steps: RoadmapStep[];
  tags?: string[];
  difficulty?: string;
}
