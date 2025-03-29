import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ArrowRight } from "lucide-react";
import type { Roadmap } from "@/types/roadmap";

interface CourseCardProps {
  roadmap: Pick<
    Roadmap,
    "id" | "title" | "description" | "tags" | "difficulty"
  >;
}

export function CourseCard({ roadmap }: CourseCardProps) {
  return (
    <Card className="flex flex-col h-full hover:shadow-lg transition-shadow duration-200">
      <CardHeader>
        <CardTitle className="text-lg line-clamp-1">{roadmap.title}</CardTitle>
        <CardDescription className="line-clamp-2 h-[40px]">
          {roadmap.description}
        </CardDescription>
      </CardHeader>
      <CardContent className="flex-grow">
        <div className="flex flex-wrap gap-1">
          {roadmap.difficulty && (
            <Badge variant="outline" className="text-xs">
              {roadmap.difficulty}
            </Badge>
          )}
          {roadmap.tags?.slice(0, 3).map((tag) => (
            <Badge key={tag} variant="secondary" className="text-xs">
              {tag}
            </Badge>
          ))}
        </div>
      </CardContent>
      <CardFooter>
        <Button asChild size="sm" className="w-full">
          <Link href={`/roadmap/${roadmap.id}`}>
            View Roadmap <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
        </Button>
      </CardFooter>
    </Card>
  );
}
