import { Component, type ReactNode } from "react";
import { EmptyState } from "./EmptyState";
import { translate } from "@/lib/i18n";
import { pushLog } from "@/lib/logStore";

interface Props {
  children: ReactNode;
}
interface State {
  error: Error | null;
}

/** Route-level crash guard so one broken panel cannot blank the whole shell. */
export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: { componentStack: string }) {
    console.error("[ErrorBoundary]", error, info.componentStack);
    pushLog("error", "boundary", error.message, `${error.stack ?? ""}\n${info.componentStack}`);
  }

  render() {
    if (this.state.error) {
      return (
        <div className="p-6">
          <EmptyState variant="failed" title={translate("error.panelCrashed")} detail={this.state.error.message} />
        </div>
      );
    }
    return this.props.children;
  }
}
