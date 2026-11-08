import React, { ErrorInfo, ReactNode } from 'react';
import { RefreshCw, Trash2, AlertTriangle, ShieldCheck } from 'lucide-react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class GlobalErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error, errorInfo: null };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Telegram Application Crash Caught by GlobalErrorBoundary:', error, errorInfo);
    this.setState({ errorInfo });
  }

  private handleHardReset = () => {
    try {
      // Clear localStorage and session cache safely
      localStorage.clear();
      sessionStorage.clear();
      // Unregister all service workers
      if ('serviceWorker' in navigator) {
        navigator.serviceWorker.getRegistrations().then((registrations) => {
          for (const registration of registrations) {
            registration.unregister();
          }
        });
      }
      // Clear Cache API
      if ('caches' in window) {
        caches.keys().then((names) => {
          for (const name of names) {
            caches.delete(name);
          }
        });
      }
    } catch (e) {
      console.error('Error during hard reset:', e);
    }
    // Force reload bypassing browser cache
    window.location.href = window.location.origin + '?reset=' + Date.now();
  };

  private handleQuickReload = () => {
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div
          dir="rtl"
          style={{
            fontFamily: "'Cairo', system-ui, -apple-system, sans-serif",
            background: 'linear-gradient(135deg, #0e1621 0%, #17212b 100%)',
          }}
          className="fixed inset-0 z-[99999] flex items-center justify-center p-4 text-white select-none"
        >
          <div className="max-w-md w-full bg-[#182533] border border-white/10 rounded-2xl p-6 shadow-2xl text-center space-y-4">
            <div className="w-16 h-16 rounded-full bg-rose-500/20 text-rose-400 border border-rose-500/30 flex items-center justify-center mx-auto">
              <AlertTriangle className="w-8 h-8" />
            </div>

            <div className="space-y-1.5">
              <h2 className="text-xl font-bold text-white">حدث خطأ في تحميل الذاكرة أو البيانات</h2>
              <p className="text-xs text-gray-400 leading-relaxed">
                تم رصد تعارض في ملفات التخزين المؤقت القديمة (Cache) أو بيانات الجلسة السابقة. يمكنك استعادة النظام فوراً بنقرة واحدة.
              </p>
            </div>

            {this.state.error && (
              <div className="bg-black/40 border border-white/5 rounded-xl p-3 text-right max-h-28 overflow-y-auto">
                <code className="text-[11px] font-mono text-rose-300 break-all leading-tight block">
                  {this.state.error.toString()}
                </code>
              </div>
            )}

            <div className="pt-2 flex flex-col gap-2.5">
              <button
                type="button"
                onClick={this.handleHardReset}
                className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white text-sm font-bold flex items-center justify-center gap-2 shadow-lg transition-all active:scale-98"
              >
                <Trash2 className="w-4 h-4" />
                <span>إصلاح تلقائي ومسح الكاش التالف</span>
              </button>

              <button
                type="button"
                onClick={this.handleQuickReload}
                className="w-full py-2.5 px-4 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-gray-300 text-xs font-semibold flex items-center justify-center gap-2 transition-all"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>إعادة تحميل الصفحة</span>
              </button>
            </div>

            <div className="pt-2 text-[10px] text-gray-500 flex items-center justify-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>نظام الاسترداد الذكي • Telegram Web DrKLO Build</span>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
