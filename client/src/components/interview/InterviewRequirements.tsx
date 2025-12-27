"use client";

import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { BriefcaseIcon, CodeIcon, TargetIcon, TrendingUpIcon, ClipboardListIcon, StickyNoteIcon, AlertCircleIcon, CheckCircle2Icon } from "lucide-react";

// Type definitions matching Python models
export interface InterviewPreference {
  experience_level: string[];
  job_role: string;
  tech_stack: string[];
  interview_type: string;
  focus_area: string[];
}

export interface UserConfirmations {
  notes?: string;
}

export interface MissingInfo {
  missing_info: string[];
  question: string;
}

export interface ReqGathringModel {
  interview_preference: InterviewPreference;
  user_confirmations: UserConfirmations;
  missing_info?: MissingInfo;
}

interface InterviewRequirementsProps {
  requirements: ReqGathringModel;
}

export const InterviewRequirements = ({ requirements }: InterviewRequirementsProps) => {
  if (!requirements) return null;

  const { interview_preference, user_confirmations, missing_info } = requirements;
  const { experience_level, job_role, tech_stack, interview_type, focus_area } = interview_preference;
  const { notes } = user_confirmations;

  // Check if requirements are complete
  const isComplete = !missing_info || missing_info.missing_info.length === 0;

  return (
    <Card className="w-full border-primary/20 shadow-lg">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-xl">
          {isComplete ? <CheckCircle2Icon className="size-5 text-green-500" /> : <ClipboardListIcon className="size-5 text-primary" />}
          Interview Requirements
        </CardTitle>
        <CardDescription>{isComplete ? "Your personalized interview preparation plan is ready" : "Gathering your interview preparation details"}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Missing Information Alert */}
        {missing_info && missing_info.missing_info.length > 0 && (
          <>
            <Alert variant="default" className="border-yellow-500/50 bg-yellow-500/10">
              <AlertCircleIcon className="size-4 text-yellow-500" />
              <AlertDescription className="ml-2">
                <p className="font-semibold text-sm mb-1">{missing_info.question}</p>
                <div className="flex flex-wrap gap-1 mt-2">
                  {missing_info.missing_info.map((field, i) => (
                    <Badge key={i} variant="outline" className="text-xs border-yellow-500/50">
                      {field}
                    </Badge>
                  ))}
                </div>
              </AlertDescription>
            </Alert>
            <Separator className="my-3" />
          </>
        )}

        {/* Job Role */}
        {job_role && (
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm font-semibold text-foreground">
              <BriefcaseIcon className="size-4 text-primary" />
              Target Role
            </div>
            <div className="ml-6">
              <Badge variant="default" className="text-sm px-3 py-1">
                {job_role}
              </Badge>
            </div>
          </div>
        )}

        {job_role && <Separator className="my-3" />}

        {/* Experience Level */}
        {experience_level && experience_level.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm font-semibold text-foreground">
              <TrendingUpIcon className="size-4 text-primary" />
              Experience Level
            </div>
            <div className="flex flex-wrap gap-2 ml-6">
              {experience_level.map((level, i) => (
                <Badge key={i} variant="secondary" className="capitalize">
                  {level}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {experience_level && experience_level.length > 0 && <Separator className="my-3" />}

        {/* Tech Stack */}
        {tech_stack && tech_stack.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm font-semibold text-foreground">
              <CodeIcon className="size-4 text-primary" />
              Technical Stack
            </div>
            <div className="flex flex-wrap gap-2 ml-6">
              {tech_stack.map((tech, i) => (
                <Badge key={i} variant="outline" className="font-mono text-xs">
                  {tech}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {tech_stack && tech_stack.length > 0 && <Separator className="my-3" />}

        {/* Interview Type */}
        {interview_type && (
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm font-semibold text-foreground">
              <ClipboardListIcon className="size-4 text-primary" />
              Interview Type
            </div>
            <div className="ml-6">
              <Badge variant="secondary" className="capitalize px-3 py-1">
                {interview_type}
              </Badge>
            </div>
          </div>
        )}

        {interview_type && <Separator className="my-3" />}

        {/* Focus Areas */}
        {focus_area && focus_area.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm font-semibold text-foreground">
              <TargetIcon className="size-4 text-primary" />
              Focus Areas
            </div>
            <div className="flex flex-wrap gap-2 ml-6">
              {focus_area.map((area, i) => (
                <Badge key={i} variant="default" className="bg-primary/10 text-primary hover:bg-primary/20">
                  {area}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Notes */}
        {notes && (
          <>
            <Separator className="my-3" />
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm font-semibold text-foreground">
                <StickyNoteIcon className="size-4 text-primary" />
                Additional Notes
              </div>
              <div className="ml-6 text-sm text-muted-foreground bg-muted/50 rounded-md p-3 border border-border">
                <p className="whitespace-pre-wrap">{notes}</p>
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
};
