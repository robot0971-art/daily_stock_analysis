import type React from 'react';
import { useEffect, useMemo, useState } from 'react';
import { Badge, Card, StatusDot } from '../common';
import { DashboardPanelHeader } from '../dashboard';
import type { TaskInfo } from '../../types/analysis';

interface TaskItemProps {
  task: TaskInfo;
  now: number;
}

const getTaskDisplayName = (task: TaskInfo): string => {
  if (task.stockCode === 'market_review') {
    return '시장 리뷰';
  }
  return task.stockName || task.stockCode;
};

const formatElapsed = (task: TaskInfo, now: number): string | null => {
  const source = task.startedAt || task.createdAt;
  const started = Date.parse(source);
  if (!Number.isFinite(started)) return null;

  const elapsedSeconds = Math.max(0, Math.floor((now - started) / 1000));
  const minutes = Math.floor(elapsedSeconds / 60);
  const seconds = elapsedSeconds % 60;

  if (minutes <= 0) return `경과 ${seconds}초`;
  return `경과 ${minutes}분 ${seconds.toString().padStart(2, '0')}초`;
};

const getLongRunningHint = (task: TaskInfo, now: number): string | null => {
  if (task.status !== 'processing') return null;

  const source = task.startedAt || task.createdAt;
  const started = Date.parse(source);
  if (!Number.isFinite(started)) return null;

  const elapsedSeconds = Math.max(0, Math.floor((now - started) / 1000));
  const progress = task.progress || 0;
  const inLlmStage = progress >= 64 && progress < 94;

  if (!inLlmStage && elapsedSeconds < 45) return null;
  return 'AI 리포트 작성 단계는 보통 1~2분 걸릴 수 있습니다.';
};

const TaskItem: React.FC<TaskItemProps> = ({ task, now }) => {
  const isPending = task.status === 'pending';
  const isProcessing = task.status === 'processing';
  const statusLabel = isProcessing ? '분석 중' : '대기 중';
  const statusVariant = isProcessing ? 'info' : 'default';
  const statusTone = isProcessing ? 'info' : 'neutral';
  const progress = Math.max(0, Math.min(100, task.progress || 0));
  const elapsed = formatElapsed(task, now);
  const longRunningHint = getLongRunningHint(task, now);

  return (
    <div className="home-subpanel flex items-start gap-3 px-3 py-2.5">
      <div className="shrink-0 pt-1">
        {isProcessing ? (
          <StatusDot tone="info" pulse className="h-2.5 w-2.5" aria-label="작업 진행 중" />
        ) : isPending ? (
          <StatusDot tone="neutral" className="h-2.5 w-2.5" aria-label="작업 대기 중" />
        ) : null}
      </div>

      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
          <span className="truncate text-sm font-medium text-foreground">
            {getTaskDisplayName(task)}
          </span>
          <span className="text-xs text-muted-text">
            {task.stockCode}
          </span>
          {elapsed ? (
            <span className="text-[11px] tabular-nums text-muted-text">
              {elapsed}
            </span>
          ) : null}
        </div>

        {task.message ? (
          <p className="mt-1 whitespace-normal break-words text-xs leading-5 text-secondary-text">
            {task.message}
          </p>
        ) : null}

        {longRunningHint ? (
          <p className="mt-1 text-[11px] leading-5 text-cyan">
            {longRunningHint}
          </p>
        ) : null}

        <div className="mt-2 flex items-center gap-2">
          <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-white/8">
            <div
              className="h-full rounded-full bg-cyan transition-[width] duration-300 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
          <span className="shrink-0 text-[11px] tabular-nums text-muted-text">
            {progress}%
          </span>
        </div>
      </div>

      <div className="shrink-0">
        <Badge
          variant={statusVariant}
          className="min-w-[4.75rem] justify-center gap-1.5 shadow-none"
          aria-label={`작업 상태: ${statusLabel}`}
        >
          <StatusDot tone={statusTone} pulse={isProcessing} className="h-1.5 w-1.5" />
          {statusLabel}
        </Badge>
      </div>
    </div>
  );
};

interface TaskPanelProps {
  tasks: TaskInfo[];
  visible?: boolean;
  title?: string;
  className?: string;
}

export const TaskPanel: React.FC<TaskPanelProps> = ({
  tasks,
  visible = true,
  title = '분석 작업',
  className = '',
}) => {
  const activeTasks = useMemo(
    () => tasks.filter((task) => task.status === 'pending' || task.status === 'processing'),
    [tasks],
  );
  const [now, setNow] = useState(() => Date.now());

  useEffect(() => {
    if (activeTasks.length === 0) return undefined;
    const timer = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(timer);
  }, [activeTasks.length]);

  if (!visible || activeTasks.length === 0) {
    return null;
  }

  const pendingCount = activeTasks.filter((task) => task.status === 'pending').length;
  const processingCount = activeTasks.filter((task) => task.status === 'processing').length;

  return (
    <Card
      variant="bordered"
      padding="none"
      className={`home-panel-card overflow-hidden ${className}`}
    >
      <div className="border-b border-subtle px-3 py-3">
        <DashboardPanelHeader
          className="mb-0"
          title={title}
          titleClassName="text-sm font-medium"
          leading={(
            <svg className="h-4 w-4 text-cyan" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
          )}
          headingClassName="items-center"
          actions={(
            <div className="flex items-center gap-2 text-xs text-muted-text">
              {processingCount > 0 ? (
                <span className="flex items-center gap-1">
                  <StatusDot tone="info" pulse className="h-1.5 w-1.5" aria-label="진행 중 작업" />
                  {processingCount} 진행 중
                </span>
              ) : null}
              {pendingCount > 0 ? (
                <span className="flex items-center gap-1">
                  <StatusDot tone="neutral" className="h-1.5 w-1.5" aria-label="대기 중 작업" />
                  {pendingCount} 대기 중
                </span>
              ) : null}
            </div>
          )}
        />
      </div>

      <div className="max-h-64 overflow-y-auto p-2">
        <div className="space-y-2">
          {activeTasks.map((task) => (
            <TaskItem key={task.taskId} task={task} now={now} />
          ))}
        </div>
      </div>
    </Card>
  );
};

export default TaskPanel;
