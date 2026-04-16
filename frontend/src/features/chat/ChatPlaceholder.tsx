import { MessageCircle } from 'lucide-react';

export function ChatPlaceholder() {
  return (
    <div className="flex h-full flex-col items-center justify-center bg-muted/30 p-6">
      <div className="text-center">
        <MessageCircle className="mx-auto mb-4 h-16 w-16 text-muted-foreground/50" />
        <h3 className="mb-2 text-lg font-medium">AI Assistant</h3>
        <p className="mb-4 text-sm text-muted-foreground">
          Log interaction details via chat
        </p>
        <div className="rounded-lg border bg-card p-4 text-left text-sm text-muted-foreground">
          <p className="mb-2 font-medium text-foreground">Try saying:</p>
          <ul className="list-inside list-disc space-y-1">
            <li>"Met Dr. Smith today, discussed OncoBoost efficacy"</li>
            <li>"Schedule a follow-up with Dr. Patel next week"</li>
            <li>"Show recent interactions with Dr. Kumar"</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
