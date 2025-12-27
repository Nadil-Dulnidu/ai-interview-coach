"use client";

import { useState } from "react";
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
  const { isSignedIn, isLoaded } = useAuth();

  const { user } = useUser();

  const { messages, sendMessage, status } = useChat({
    transport: new DefaultChatTransport({
      api: `${process.env.BACKEND_URL}/travel-system/chat`,
      body: {
        thread_id: threadId,
        resume: isInterrupted,
      },
    }),
    // Note: messageMetadata is a custom property from our server
    onFinish: (data: { messageMetadata?: { interrupt?: boolean; interruptMessage?: string } } & Record<string, unknown>) => {
      const { messageMetadata } = data;
      // Check if this is an interrupt
      if (messageMetadata?.interrupt) {
        setIsInterrupted(true);
        setInterruptMessage(messageMetadata.interruptMessage || "");
      } else {
        setIsInterrupted(false);
        setInterruptMessage("");
      }
    },
  });

  const handleSubmit = (message: { text: string }) => {
    if (!message.text || !message.text.trim()) {
      return;
    }

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

      if (dataType === "requirements" && dataPart.data) {
        return (
          <div key={`${messageId}-${index}`} className="my-4">
            <InterviewRequirements requirements={dataPart.data as unknown as ReqGathringModel} />
          </div>
        );
      }

      if (dataType === "evaluation" && dataPart.data) {
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
    <div className="mx-auto h-screen p-6 relative container">
      <div className="h-full flex flex-col">
        {/* Header */}
        <Header />
        {/* chat body */}
        <div className="flex flex-col flex-1 w-full max-w-4xl mx-auto">
          {/* Conversation Area */}
          <Conversation className="flex-1 text-lg ">
            <ConversationContent>
              {messages.length === 0 && (
                <div className="flex flex-col items-center justify-center h-full gap-6">
                  <div className="text-center space-y-2">
                    {isSignedIn && isLoaded ? (
                      <Greeting name={user?.firstName || "User"} className="text-3xl" showIcon={true} />
                    ) : (
                      <p className="text-3xl font-bold tracking-tight">Master your next interview.</p>
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
          {messages.length === 0 && (
            <Suggestions className="mb-4">
              <Suggestion onClick={() => handleSuggestionClick("I have a interview for Intern AI Engineer position")} suggestion="Intern AI Engineer position interview" />
              <Suggestion onClick={() => handleSuggestionClick("Can you help me prepare for a behavioral interview?")} suggestion="Behavioral interview prep" />
              <Suggestion onClick={() => handleSuggestionClick("I'd like to do a mock interview for a Software Engineering position")} suggestion="Software Engineer mock interview" />
            </Suggestions>
          )}

          {/* Input Area */}
          <PromptInput onSubmit={handleSubmit} className="mt-4">
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
              <PromptInputSubmit disabled={!input} status={status} />
            </PromptInputFooter>
          </PromptInput>
        </div>
      </div>
    </div>
  );
}

export default ChatApp;
