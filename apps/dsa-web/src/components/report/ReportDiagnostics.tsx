import type React from 'react';
import { useEffect, useMemo, useRef, useState } from 'react';
import { Activity, Check, ChevronDown, Copy } from 'lucide-react';
import { historyApi } from '../../api/history';
import type {
  ReportLanguage,
  RunDiagnosticComponent,
  RunDiagnosticComponentStatus,
  RunDiagnosticStatus,
  RunDiagnosticSummary,
} from '../../types/analysis';
import { normalizeReportLanguage } from '../../utils/reportLanguage';
import { Badge, Button, Card, StatusDot } from '../common';

interface ReportDiagnosticsProps {
  recordId?: number;
  summary?: RunDiagnosticSummary;
  language?: ReportLanguage;
}

type BadgeVariant = NonNullable<React.ComponentProps<typeof Badge>['variant']>;
type StatusTone = NonNullable<React.ComponentProps<typeof StatusDot>['tone']>;

const COMPONENT_ORDER = [
  'realtime_quote',
  'daily_data',
  'news',
  'llm',
  'notification',
  'history',
];

const TEXT = {
  ko: {
    eyebrow: '실행 진단',
    title: '데이터 신뢰도',
    loading: '진단 정보를 불러오는 중...',
    unavailable: '진단 정보를 사용할 수 없습니다',
    noComponents: '세부 진단 정보가 없습니다',
    components: '주요 경로',
    advanced: '추가 정보',
    copy: '진단 복사',
    copied: '복사됨',
    trace: 'Trace',
    task: 'Task',
    query: 'Query',
    trigger: '실행 원인',
    overall: {
      normal: '정상',
      degraded: '확인 필요',
      failed: '실패',
      unknown: '알 수 없음',
    },
    component: {
      ok: '정상',
      degraded: '확인 필요',
      failed: '실패',
      unknown: '알 수 없음',
      not_configured: '미설정',
      skipped: '건너뜀',
    },
  },
  en: {
    eyebrow: 'RUN DIAGNOSTICS',
    title: 'Data Reliability',
    loading: 'Loading diagnostics...',
    unavailable: 'Diagnostics unavailable',
    noComponents: 'No component diagnostics',
    components: 'Key Path',
    advanced: 'Advanced Fields',
    copy: 'Copy diagnostics',
    copied: 'Copied',
    trace: 'Trace',
    task: 'Task',
    query: 'Query',
    trigger: 'Trigger',
    overall: {
      normal: 'Normal',
      degraded: 'Degraded',
      failed: 'Failed',
      unknown: 'Unknown',
    },
    component: {
      ok: 'Normal',
      degraded: 'Recent failure',
      failed: 'Failed',
      unknown: 'Unknown',
      not_configured: 'Not configured',
      skipped: 'Skipped',
    },
  },
} as const;

const OVERALL_STATUS_STYLE: Record<RunDiagnosticStatus, { variant: BadgeVariant; tone: StatusTone }> = {
  normal: { variant: 'success', tone: 'success' },
  degraded: { variant: 'warning', tone: 'warning' },
  failed: { variant: 'danger', tone: 'danger' },
  unknown: { variant: 'default', tone: 'neutral' },
};

const COMPONENT_STATUS_STYLE: Record<RunDiagnosticComponentStatus, { variant: BadgeVariant; tone: StatusTone }> = {
  ok: { variant: 'success', tone: 'success' },
  degraded: { variant: 'warning', tone: 'warning' },
  failed: { variant: 'danger', tone: 'danger' },
  unknown: { variant: 'default', tone: 'neutral' },
  not_configured: { variant: 'default', tone: 'neutral' },
  skipped: { variant: 'default', tone: 'neutral' },
};

const compactId = (value?: string): string | null => {
  const text = (value || '').trim();
  if (!text) return null;
  if (text.length <= 28) return text;
  return `${text.slice(0, 10)}...${text.slice(-8)}`;
};

const KO_COMPONENT_LABELS: Record<string, string> = {
  realtime_quote: '실시간 시세',
  daily_data: '일봉 데이터',
  news: '뉴스 검색',
  llm: 'LLM',
  notification: '알림',
  history: '기록 저장',
};

const normalizeLegacyDiagnosticText = (value?: string): string => {
  let text = (value || '').trim();
  if (!text) return text;

  text = text
    .replace(/实时行情\s*([^，\s]+)\s*成功，前置数据源失败后已继续/g, '실시간 시세: $1 성공, 이전 데이터 소스 실패 후 계속 진행했습니다')
    .replace(/日线数据\s*([^，\s]+)\s*成功，前置数据源失败后已继续/g, '일봉 데이터: $1 성공, 이전 데이터 소스 실패 후 계속 진행했습니다')
    .replace(/实时行情\s*([^，\s]+)\s*成功/g, '실시간 시세: $1 성공')
    .replace(/日线数据\s*([^，\s]+)\s*成功/g, '일봉 데이터: $1 성공')
    .replace(/新闻检索返回\s*(\d+)\s*条结果/g, '뉴스 검색 결과 $1건을 찾았습니다')
    .replace(/LLM\s+([^，\s]+)\s*成功，期间发生过失败或模型切换/g, 'LLM $1 성공, 중간에 실패 또는 모델 전환이 있었습니다')
    .replace(/LLM\s+([^，\s]+)\s*成功/g, 'LLM $1 성공');

  const replacements: Array<[RegExp, string]> = [
    [/旧报告或诊断证据不足，无法判断本次运行状态/g, '이전 보고서이거나 진단 근거가 부족해 이번 실행 상태를 판단할 수 없습니다'],
    [/可用诊断证据不足，无法判断本次运行状态/g, '사용 가능한 진단 근거가 부족해 이번 실행 상태를 판단할 수 없습니다'],
    [/实时行情/g, '실시간 시세'],
    [/日线数据/g, '일봉 데이터'],
    [/新闻搜索/g, '뉴스 검색'],
    [/新闻检索/g, '뉴스 검색'],
    [/新闻搜索无结果/g, '뉴스 검색 결과가 없습니다'],
    [/新闻检索未记录原始证据，可能未尝试或未启用/g, '뉴스 원본 근거가 기록되지 않았습니다'],
    [/新闻搜索未记录诊断信息/g, '뉴스 검색 진단 정보가 기록되지 않았습니다'],
    [/前置数据源失败后已继续/g, '이전 데이터 소스 실패 후 계속 진행했습니다'],
    [/通知未配置或本次跳过/g, '알림이 설정되지 않았거나 이번 실행에서 건너뛰었습니다'],
    [/通知结果未记录/g, '알림 결과가 기록되지 않았습니다'],
    [/通知发送成功/g, '알림 전송 성공'],
    [/部分通知渠道失败，其余渠道已发送/g, '일부 알림 채널이 실패했고 나머지 채널은 전송되었습니다'],
    [/通知失败：/g, '알림 실패: '],
    [/通知/g, '알림'],
    [/历史保存/g, '기록 저장'],
    [/报告历史已保存/g, '분석 기록이 저장되었습니다'],
    [/报告历史保存失败/g, '분석 기록 저장 실패'],
    [/未记录诊断信息/g, '진단 정보가 기록되지 않았습니다'],
    [/所有数据源尝试失败/g, '모든 데이터 소스 시도가 실패했습니다'],
    [/失败：/g, '실패: '],
    [/成功/g, '성공'],
    [/未知错误/g, '알 수 없는 오류'],
  ];

  return replacements.reduce((current, [pattern, replacement]) => (
    current.replace(pattern, replacement)
  ), text);
};

const normalizeDiagnosticComponent = (component: RunDiagnosticComponent): RunDiagnosticComponent => ({
  ...component,
  label: KO_COMPONENT_LABELS[component.key] || normalizeLegacyDiagnosticText(component.label),
  message: normalizeLegacyDiagnosticText(component.message),
});

const getOrderedComponents = (
  components?: Record<string, RunDiagnosticComponent>,
): RunDiagnosticComponent[] => {
  const items = Object.values(components || {});
  const ordered = COMPONENT_ORDER
    .map((key) => items.find((component) => component.key === key))
    .filter((component): component is RunDiagnosticComponent => Boolean(component));
  const remaining = items.filter((component) => !COMPONENT_ORDER.includes(component.key));
  return [...ordered, ...remaining];
};

/**
 * Collapsed report diagnostics for self-hosted troubleshooting.
 */
export const ReportDiagnostics: React.FC<ReportDiagnosticsProps> = ({
  recordId,
  summary,
  language = 'ko',
}) => {
  const reportLanguage = normalizeReportLanguage(language);
  const text = reportLanguage === 'en' ? TEXT.en : TEXT.ko;
  const [fetchState, setFetchState] = useState<{
    recordId?: number;
    summary: RunDiagnosticSummary | null;
    failed: boolean;
  }>({
    summary: null,
    failed: false,
  });
  const [copied, setCopied] = useState(false);
  const resetCopiedTimerRef = useRef<number | null>(null);

  useEffect(() => {
    if (summary || !recordId) {
      return undefined;
    }

    let active = true;
    void historyApi.getDiagnostics(recordId)
      .then((result) => {
        if (active) {
          setFetchState({
            recordId,
            summary: result,
            failed: false,
          });
        }
      })
      .catch(() => {
        if (active) {
          setFetchState({
            recordId,
            summary: null,
            failed: true,
          });
        }
      });

    return () => {
      active = false;
    };
  }, [recordId, summary]);

  useEffect(() => () => {
    if (resetCopiedTimerRef.current !== null) {
      window.clearTimeout(resetCopiedTimerRef.current);
    }
  }, []);

  const fetchedForRecord = recordId !== undefined && fetchState.recordId === recordId
    ? fetchState
    : null;
  const loadedSummary = summary ?? fetchedForRecord?.summary ?? null;
  const loadFailed = !summary && Boolean(fetchedForRecord?.failed);
  const isLoading = Boolean(recordId && !summary && !fetchedForRecord);

  const visibleSummary = useMemo<RunDiagnosticSummary | null>(() => {
    if (loadedSummary) {
      return loadedSummary;
    }
    if (!recordId && !summary) {
      return null;
    }
    if (!isLoading && !loadFailed) {
      return null;
    }
    return {
      status: 'unknown',
      statusLabel: text.overall.unknown,
      reason: loadFailed ? text.unavailable : text.loading,
      components: {},
      copyText: '',
    };
  }, [isLoading, loadFailed, loadedSummary, recordId, summary, text]);

  if (!visibleSummary) {
    return null;
  }

  const statusStyle = OVERALL_STATUS_STYLE[visibleSummary.status] || OVERALL_STATUS_STYLE.unknown;
  const statusLabel = text.overall[visibleSummary.status] || visibleSummary.statusLabel;
  const reason = reportLanguage === 'ko'
    ? normalizeLegacyDiagnosticText(visibleSummary.reason)
    : visibleSummary.reason;
  const components = getOrderedComponents(visibleSummary.components).map((component) => (
    reportLanguage === 'ko' ? normalizeDiagnosticComponent(component) : component
  ));
  const traceId = compactId(visibleSummary.traceId);
  const taskId = compactId(visibleSummary.taskId);
  const queryId = compactId(visibleSummary.queryId);
  const copyText = reportLanguage === 'ko'
    ? normalizeLegacyDiagnosticText(visibleSummary.copyText)
    : visibleSummary.copyText;
  const hasCopyText = Boolean(copyText && !isLoading);
  const advancedPayload = {
    traceId: visibleSummary.traceId,
    taskId: visibleSummary.taskId,
    queryId: visibleSummary.queryId,
    stockCode: visibleSummary.stockCode,
    triggerSource: visibleSummary.triggerSource,
    components: components.reduce<Record<string, Record<string, unknown>>>((payload, component) => {
      payload[component.key] = {
        status: component.status,
        message: component.message,
        details: component.details || {},
      };
      return payload;
    }, {}),
  };
  const hasAdvancedPayload = Boolean(
    visibleSummary.traceId
    || visibleSummary.taskId
    || visibleSummary.queryId
    || visibleSummary.stockCode
    || visibleSummary.triggerSource
    || components.some((component) => component.details && Object.keys(component.details).length > 0),
  );

  const copyDiagnostics = async () => {
    if (!hasCopyText || !navigator.clipboard?.writeText) {
      return;
    }

    try {
      await navigator.clipboard.writeText(copyText);
      setCopied(true);
      if (resetCopiedTimerRef.current !== null) {
        window.clearTimeout(resetCopiedTimerRef.current);
      }
      resetCopiedTimerRef.current = window.setTimeout(() => {
        setCopied(false);
        resetCopiedTimerRef.current = null;
      }, 2000);
    } catch (err) {
      console.error('Copy diagnostics failed:', err);
    }
  };

  return (
    <Card variant="bordered" padding="none" className="home-panel-card text-left">
      <details data-testid="run-diagnostics" className="group">
        <summary className="flex cursor-pointer list-none items-center justify-between gap-3 px-4 py-3">
          <div className="flex min-w-0 items-center gap-3">
            <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-cyan/10 text-cyan">
              <Activity className="h-4 w-4" aria-hidden="true" />
            </span>
            <span className="min-w-0">
              <span className="label-uppercase">{text.eyebrow}</span>
              <span className="mt-0.5 block truncate text-base font-semibold text-foreground">
                {text.title}
              </span>
            </span>
          </div>
          <span className="flex shrink-0 items-center gap-2">
            {isLoading ? (
              <span className="home-spinner h-3.5 w-3.5 animate-spin border-2" aria-hidden="true" />
            ) : null}
            <Badge variant={statusStyle.variant} className="gap-1.5 shadow-none">
              <StatusDot tone={statusStyle.tone} className="h-1.5 w-1.5" />
              {statusLabel}
            </Badge>
            <ChevronDown className="h-4 w-4 text-muted-text transition-transform group-open:rotate-180" aria-hidden="true" />
          </span>
        </summary>

        <div className="home-divider space-y-4 border-t px-4 pb-4 pt-3">
          <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
            <div className="min-w-0 space-y-2">
              <p className="text-sm leading-6 text-foreground">
                {reason}
              </p>
              <div className="flex flex-wrap items-center gap-2 text-xs text-muted-text">
                {traceId ? (
                  <span className="home-accent-chip px-2 py-0.5 font-mono">
                    {text.trace}: {traceId}
                  </span>
                ) : null}
                {taskId ? (
                  <span className="home-accent-chip px-2 py-0.5 font-mono">
                    {text.task}: {taskId}
                  </span>
                ) : null}
                {queryId ? (
                  <span className="home-accent-chip px-2 py-0.5 font-mono">
                    {text.query}: {queryId}
                  </span>
                ) : null}
                {visibleSummary.triggerSource ? (
                  <span className="home-accent-chip px-2 py-0.5">
                    {text.trigger}: {visibleSummary.triggerSource}
                  </span>
                ) : null}
              </div>
            </div>
            <Button
              variant="ghost"
              size="xsm"
              disabled={!hasCopyText}
              onClick={() => void copyDiagnostics()}
              aria-label={copied ? text.copied : text.copy}
              className="shrink-0"
            >
              {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
              {copied ? text.copied : text.copy}
            </Button>
          </div>

          <div>
            <span className="label-uppercase">{text.components}</span>
            <div className="mt-2 grid grid-cols-1 gap-2 md:grid-cols-2">
              {components.length > 0 ? components.map((component) => {
                const componentStyle = COMPONENT_STATUS_STYLE[component.status] || COMPONENT_STATUS_STYLE.unknown;
                const componentLabel = text.component[component.status] || component.status;
                return (
                  <div key={component.key} className="home-subpanel p-3">
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-foreground">
                          {component.label}
                        </p>
                        <p className="mt-1 text-xs leading-5 text-secondary-text">
                          {component.message}
                        </p>
                      </div>
                      <Badge variant={componentStyle.variant} className="shrink-0 gap-1.5 shadow-none">
                        <StatusDot tone={componentStyle.tone} className="h-1.5 w-1.5" />
                        {componentLabel}
                      </Badge>
                    </div>
                  </div>
                );
              }) : (
                <p className="home-subpanel p-3 text-sm text-secondary-text">
                  {text.noComponents}
                </p>
              )}
            </div>
          </div>

          {hasAdvancedPayload ? (
            <details className="home-subpanel group/advanced p-3">
              <summary className="flex cursor-pointer list-none items-center justify-between gap-3">
                <span className="text-sm font-medium text-foreground">{text.advanced}</span>
                <ChevronDown className="h-4 w-4 text-muted-text transition-transform group-open/advanced:rotate-180" aria-hidden="true" />
              </summary>
              <pre className="home-trace-pre home-trace-pre-content mt-3 max-h-80 overflow-auto rounded-lg bg-base p-3 text-left font-mono text-xs text-foreground">
                {JSON.stringify(advancedPayload, null, 2)}
              </pre>
            </details>
          ) : null}
        </div>
      </details>
    </Card>
  );
};
