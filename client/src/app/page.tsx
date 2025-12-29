"use client";

import { useState, useEffect, useRef, useCallback, useMemo} from "react";
import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport, ToolUIPart } from "ai";
import { nanoid } from "nanoid";
import { Conversation, ConversationContent, ConversationScrollButton } from "@/components/ai-elements/conversation";
import { Message, MessageContent, MessageResponse } from "@/components/ai-elements/message";
import { PromptInput, PromptInputBody, PromptInputSubmit, PromptInputTextarea, PromptInputFooter } from "@/components/ai-elements/prompt-input";
import { Loader } from "@/components/ai-elements/loader";
import { Tool, ToolHeader, ToolContent, ToolInput, ToolOutput } from "@/components/ai-elements/tool";
import { Suggestions, Suggestion } from "@/components/ai-elements/suggestion";
import { InterviewRequirements, type ReqGathringModel } from "@/components/interview/InterviewRequirements";
import { InterviewEvaluation, type InterviewEvaluation as InterviewEvaluationType } from "@/components/interview/InterviewEvaluation";
import Greeting from "@/components/Greeting";
import Header from "@/components/Header";
import { useUser, useAuth } from "@clerk/nextjs";
import { BACKEND_URL } from "@/config/env";

// Type definitions for message parts
type TextPart = {
  type: "text";
  text: string;
};

type ToolPart = {
  type: `tool-${string}`;
  input?: ToolUIPart["input"];
  output?: ToolUIPart["output"];
  error?: string;
  state?: ToolUIPart["state"];
};

type DataPart = {
  type: `data-${string}`;
  data?: unknown;
};

type MessagePart = TextPart | ToolPart | DataPart | { type: string; [key: string]: unknown };

function ChatApp() {
  const [input, setInput] = useState("");
  const [threadId] = useState(() => nanoid());
  const [isInterrupted, setIsInterrupted] = useState(false);
  const [interruptMessage, setInterruptMessage] = useState("");
  const { isSignedIn, isLoaded, getToken } = useAuth();
  const { user } = useUser();

  // Use a ref to store the interrupt state - this avoids closure issues
  // The ref always contains the current value and can be safely accessed in callbacks
  const isInterruptedRef = useRef(isInterrupted);

  // Keep ref in sync with state
  useEffect(() => {
    isInterruptedRef.current = isInterrupted;
  }, [isInterrupted]);
  
  // Create transport once - the body function reads from ref to get current value
  // Note: ESLint warns about ref access, but this is a false positive.
  // We're not accessing the ref during render - we're defining a callback that accesses it later.
  /* eslint-disable */
  const transport = useMemo(
    () =>
      new DefaultChatTransport({
        api: `${BACKEND_URL}/interview-coach/chat`,
        headers: async () => {
          const token = await getToken({ template: "interviewiq" });
          return {
            Authorization: `Bearer ${token}`,
          };
        },
        body: () => {
          // Access ref in callback (safe to do, not during render)
          const currentResumeValue = isInterruptedRef.current;
          return {
            thread_id: threadId,
            resume: currentResumeValue,
            user_name: user?.firstName || "",
            assistent_name: "InterviewIQ",
          };
        },
      }),
    [threadId] // Only recreate if threadId changes
  );
  // Memoize onFinish to prevent recreating on every render
  const handleFinish = useCallback(
    (
      data: {
        messageMetadata?: { interrupt?: boolean; interruptMessage?: string };
        finishReason?: string;
      } & Record<string, unknown>
    ) => {
      const { messageMetadata, finishReason } = data;

      // Check if this is an interrupt
      if (finishReason === undefined || finishReason === "interrupt") {
        setIsInterrupted(true);
        setInterruptMessage(messageMetadata?.interruptMessage || "Please provide the requested information...");
      } else if (finishReason === "stop" || finishReason === "length" || finishReason === "content-filter") {
        setIsInterrupted(false);
        setInterruptMessage("");
      }
    },
    [] // Empty deps - setIsInterrupted and setInterruptMessage are stable
  );

  const { messages, sendMessage, status } = useChat({
    transport,
    onFinish: handleFinish,
  });

  const handleSubmit = (message: { text: string }) => {
    if (!message.text || !message.text.trim()) {
      return;
    }

    // Send the message - the transport will use the current isInterrupted value
    sendMessage({
      text: message.text.trim(),
    });

    setInput("");
  };

  const handleSuggestionClick = (suggestion: string) => {
    sendMessage({ text: suggestion });
  };

  const renderMessagePart = (part: MessagePart, index: number, messageId: string) => {
    // Render text parts
    if (part.type === "text") {
      const textPart = part as TextPart;
      return (
        <Message key={`${messageId}-${index}`} from="assistant">
          <MessageContent>
            <MessageResponse>{textPart.text}</MessageResponse>
          </MessageContent>
        </Message>
      );
    }

    // Render tool calls
    if (part.type.startsWith("tool-")) {
      const toolPart = part as ToolPart;
      const toolName = toolPart.type.slice(5); // Remove 'tool-' prefix
      return (
        <Tool key={`${messageId}-${index}`}>
          <ToolHeader
            title={toolName.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
            type={toolPart.type as `tool-${string}`}
            state={(toolPart.state || "input-available") as ToolUIPart["state"]}
          />
          <ToolContent>
            {toolPart.input ? <ToolInput input={toolPart.input!} /> : null}
            {toolPart.output ? <ToolOutput output={toolPart.output!} errorText={undefined} /> : null}
            {toolPart.error ? <ToolOutput output={undefined} errorText={toolPart.error} /> : null}
          </ToolContent>
        </Tool>
      );
    }

    // Render custom data parts (Vercel protocol compliant)
    if (part.type.startsWith("data-")) {
      const dataPart = part as DataPart;
      const dataType = dataPart.type.slice(5); // Remove 'data-' prefix

      // Handle interrupt data (don't render, it's handled in useEffect)
      if (dataType === "interrupt") {
        return null; // Don't render interrupt data parts
      }

      if (dataType === "final_user_requirements" && dataPart.data) {
        return (
          <div key={`${messageId}-${index}`} className="my-4">
            <InterviewRequirements requirements={dataPart.data as unknown as ReqGathringModel} />
          </div>
        );
      }

      if (dataType === "final_interview_evaluation" && dataPart.data) {
        return (
          <div key={`${messageId}-${index}`} className="my-4">
            <InterviewEvaluation evaluation={dataPart.data as unknown as InterviewEvaluationType} />
          </div>
        );
      }
    }

    return null;
  };

  return (
    <div className="mx-auto h-screen px-6 py-4 relative container overflow-hidden">
      <div className="h-full flex flex-col">
        {/* Header */}
        <Header />
        {/* chat body */}
        <div className="flex flex-col flex-1 min-h-0 w-full max-w-4xl mx-auto ">
          {/* Conversation Area */}
          <Conversation className="flex-1 text-lg flow min-h-0 scrollbar-thin">
            <ConversationContent>
              {messages.length === 0 && (
                <div className="flex flex-col items-center justify-center h-full gap-6">
                  <div className="text-center space-y-2">
                    {isSignedIn && isLoaded ? (
                      <Greeting name={user?.firstName || "User"} className="text-3xl" showIcon={false} />
                    ) : (
                      <p className="text-3xl font-semibold tracking-tight">Master your next interview.</p>
                    )}
                    <p className="text-muted-foreground">Practice behavioral and technical questions with personalized feedback from your AI coach.</p>
                  </div>
                </div>
              )}

              {messages.map((message) => (
                <div key={message.id}>
                  {message.role === "user" ? (
                    <Message from="user">
                      <MessageContent>
                        <MessageResponse>{message.parts.find((p) => p.type === "text")?.text || ""}</MessageResponse>
                      </MessageContent>
                    </Message>
                  ) : (
                    message.parts.map((part, i) => renderMessagePart(part, i, message.id))
                  )}
                </div>
              ))}

              {/* Loading State */}
              {status === "submitted" && (
                <Message from="assistant">
                  <MessageContent>
                    <div className="flex items-center gap-2">
                      <Loader />
                      <span className="text-sm text-muted-foreground">{isInterrupted ? "Processing your response..." : "Thinking..."}</span>
                    </div>
                  </MessageContent>
                </Message>
              )}
            </ConversationContent>

            {/* Scroll to Bottom Button */}
            <ConversationScrollButton />
          </Conversation>

          {/* Suggestions (only show when no messages) */}
          {(messages.length === 0 && isSignedIn) && (
            <Suggestions className="mb-4 shrink-0">
              <Suggestion onClick={() => handleSuggestionClick("I have a interview for Intern AI Engineer position")} suggestion="Intern AI Engineer position interview" />
              <Suggestion onClick={() => handleSuggestionClick("Can you help me prepare for a behavioral interview?")} suggestion="Behavioral interview prep" />
              <Suggestion onClick={() => handleSuggestionClick("I'd like to do a mock interview for a Software Engineering position")} suggestion="Software Engineer mock interview" />
            </Suggestions>
          )}

          {/* Input Area */}
          <PromptInput onSubmit={handleSubmit} className="mt-4 shrink-0">
            {/* Textarea */}
            <PromptInputBody>
              <PromptInputTextarea
                onChange={(e) => setInput(e.target.value)}
                value={input}
                placeholder={isInterrupted ? interruptMessage || "Please provide the requested information..." : "What type of interview would you like to practice?"}
              />
            </PromptInputBody>

            {/* Footer with Submit Button */}
            <PromptInputFooter>
              <PromptInputSubmit disabled={!input || !isSignedIn} status={status} size={"sm"} />
            </PromptInputFooter>
          </PromptInput>
        </div>
      </div>
    </div>
  );
}

export default ChatApp;
