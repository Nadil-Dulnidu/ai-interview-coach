"use client";

import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Progress } from "@/components/ui/progress";
import { TrophyIcon, CheckCircle2Icon, AlertCircleIcon, TrendingUpIcon, MessageSquareIcon, LightbulbIcon, TargetIcon, StarIcon, ThumbsUpIcon, ThumbsDownIcon } from "lucide-react";

// Type definitions matching Python models
export interface QuestionEvaluation {
  question_id: string;
  question: string;
  user_answer: string;
  expected_answer: string;
  score: number; // 0-10
  strengths: string[];
  weaknesses: string[];
  improvement_suggestions: string[];
}

export interface InterviewEvaluation {
  question_evaluations: QuestionEvaluation[];
  average_score: number; // 0-10
  overall_strengths: string[];
  overall_weaknesses: string[];
  hire_recommendation: "Strong Hire" | "Hire" | "No Hire" | "Strong No Hire";
}

interface InterviewEvaluationProps {
  evaluation: InterviewEvaluation;
}

// Helper function to get recommendation styling
const getRecommendationStyle = (recommendation: string) => {
  switch (recommendation) {
    case "Strong Hire":
      return {
        variant: "default" as const,
        className: "bg-green-600 hover:bg-green-700",
        icon: TrophyIcon,
        color: "text-green-600",
      };
    case "Hire":
      return {
        variant: "default" as const,
        className: "bg-blue-600 hover:bg-blue-700",
        icon: ThumbsUpIcon,
        color: "text-blue-600",
      };
    case "No Hire":
      return {
        variant: "secondary" as const,
        className: "bg-orange-600 hover:bg-orange-700 text-white",
        icon: ThumbsDownIcon,
        color: "text-orange-600",
      };
    case "Strong No Hire":
      return {
        variant: "destructive" as const,
        className: "",
        icon: AlertCircleIcon,
        color: "text-red-600",
      };
    default:
      return {
        variant: "secondary" as const,
        className: "",
        icon: MessageSquareIcon,
        color: "text-gray-600",
      };
  }
};

// Helper to get score color
const getScoreColor = (score: number) => {
  if (score >= 8) return "text-green-600";
  if (score >= 6) return "text-blue-600";
  if (score >= 4) return "text-yellow-600";
  return "text-red-600";
};

// Helper to get progress bar color
const getProgressColor = (score: number) => {
  if (score >= 8) return "bg-green-600";
  if (score >= 6) return "bg-blue-600";
  if (score >= 4) return "bg-yellow-600";
  return "bg-red-600";
};

const QuestionCard = ({ evaluation, index }: { evaluation: QuestionEvaluation; index: number }) => {
  const scorePercentage = (evaluation.score / 10) * 100;

  return (
    <div className="border rounded-lg p-4 space-y-3 bg-card">
      {/* Question Header */}
      <div className="space-y-2">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1">
            <Badge variant="outline" className="mb-2">
              Question {index + 1}
            </Badge>
            <h3 className="font-semibold text-base">{evaluation.question}</h3>
          </div>
          <div className="flex flex-col items-end gap-1">
            <span className={`text-2xl font-bold ${getScoreColor(evaluation.score)}`}>{evaluation.score.toFixed(1)}</span>
            <span className="text-xs text-muted-foreground">/ 10</span>
          </div>
        </div>
        <Progress value={scorePercentage} className="h-2" />
      </div>

      <Separator />

      {/* Answers Section */}
      <div className="space-y-3">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-sm font-semibold">
            <MessageSquareIcon className="size-4 text-primary" />
            Your Answer
          </div>
          <p className="text-sm text-muted-foreground bg-muted/50 rounded-md p-3 ml-6 border border-border">{evaluation.user_answer}</p>
        </div>

        <div className="space-y-1">
          <div className="flex items-center gap-2 text-sm font-semibold">
            <TargetIcon className="size-4 text-green-600" />
            Expected Answer
          </div>
          <p className="text-sm text-muted-foreground bg-green-50/50 dark:bg-green-950/20 rounded-md p-3 ml-6 border border-green-200 dark:border-green-900">{evaluation.expected_answer}</p>
        </div>
      </div>

      <Separator />

      {/* Strengths */}
      {evaluation.strengths.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-sm font-semibold text-green-600">
            <CheckCircle2Icon className="size-4" />
            Strengths
          </div>
          <ul className="space-y-1 ml-6">
            {evaluation.strengths.map((strength, i) => (
              <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                <span className="text-green-600 mt-0.5">✓</span>
                <span>{strength}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Weaknesses */}
      {evaluation.weaknesses.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-sm font-semibold text-orange-600">
            <AlertCircleIcon className="size-4" />
            Areas for Improvement
          </div>
          <ul className="space-y-1 ml-6">
            {evaluation.weaknesses.map((weakness, i) => (
              <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                <span className="text-orange-600 mt-0.5">⚠</span>
                <span>{weakness}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Improvement Suggestions */}
      {evaluation.improvement_suggestions.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-sm font-semibold text-blue-600">
            <LightbulbIcon className="size-4" />
            Suggestions
          </div>
          <ul className="space-y-1 ml-6">
            {evaluation.improvement_suggestions.map((suggestion, i) => (
              <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                <span className="text-blue-600 mt-0.5">💡</span>
                <span>{suggestion}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export const InterviewEvaluation = ({ evaluation }: InterviewEvaluationProps) => {
  if (!evaluation) return null;

  const { question_evaluations, average_score, overall_strengths, overall_weaknesses, hire_recommendation } = evaluation;

  const recommendationStyle = getRecommendationStyle(hire_recommendation);
  const RecommendationIcon = recommendationStyle.icon;
  const averagePercentage = (average_score / 10) * 100;

  return (
    <Card className="w-full border-primary/20 shadow-lg">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2 text-xl">
          <TrophyIcon className="size-6 text-yellow-500" />
          Interview Evaluation
        </CardTitle>
        <CardDescription>Your comprehensive performance assessment</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Overall Score & Recommendation */}
        <Alert className="border-2">
          <div className="flex items-center justify-between w-full">
            <div className="flex items-center gap-3">
              <RecommendationIcon className={`size-8 ${recommendationStyle.color}`} />
              <div>
                <p className="font-semibold text-lg">Final Recommendation</p>
                <Badge variant={recommendationStyle.variant} className={`${recommendationStyle.className} mt-1`}>
                  {hire_recommendation}
                </Badge>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-muted-foreground mb-1">Average Score</p>
              <p className={`text-4xl font-bold ${getScoreColor(average_score)}`}>{average_score.toFixed(1)}</p>
              <p className="text-xs text-muted-foreground">/ 10</p>
            </div>
          </div>
        </Alert>

        <Progress value={averagePercentage} className="h-3" />

        <Separator />

        {/* Overall Strengths */}
        {overall_strengths.length > 0 && (
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-base font-semibold text-green-600">
              <TrendingUpIcon className="size-5" />
              Overall Strengths
            </div>
            <div className="ml-7 space-y-2">
              {overall_strengths.map((strength, i) => (
                <div key={i} className="flex items-start gap-2 text-sm">
                  <StarIcon className="size-4 text-green-600 mt-0.5 fill-green-600" />
                  <span>{strength}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Overall Weaknesses */}
        {overall_weaknesses.length > 0 && (
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-base font-semibold text-orange-600">
              <AlertCircleIcon className="size-5" />
              Areas to Focus On
            </div>
            <div className="ml-7 space-y-2">
              {overall_weaknesses.map((weakness, i) => (
                <div key={i} className="flex items-start gap-2 text-sm">
                  <span className="text-orange-600 mt-0.5">⚠</span>
                  <span>{weakness}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <Separator />

        {/* Individual Question Evaluations */}
        <div className="space-y-3">
          <h3 className="text-base font-semibold">Detailed Question Analysis</h3>
          <div className="space-y-4">
            {question_evaluations.map((qEval, index) => (
              <QuestionCard key={qEval.question_id} evaluation={qEval} index={index} />
            ))}
          </div>
        </div>

        {/* Next Steps */}
        <div className="mt-6 p-4 rounded-lg bg-muted/50 border border-border space-y-2">
          <p className="text-sm font-semibold flex items-center gap-2">
            <LightbulbIcon className="size-4 text-primary" />
            Next Steps
          </p>
          <ul className="text-sm text-muted-foreground space-y-1 ml-6 list-disc">
            <li>Review the detailed feedback for each question</li>
            <li>Practice the areas highlighted for improvement</li>
            <li>Study the expected answer patterns</li>
            <li>Schedule a follow-up practice session</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
};
