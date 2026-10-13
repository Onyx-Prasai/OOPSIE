import { Memento } from 'vscode';
import { OopsieReport } from '../types/oopsie';

export interface AnalysisHistoryItem {
  errorText: string;
  report: OopsieReport;
  createdAt: number;
}

export async function addHistoryItem(
  storage: Memento,
  item: AnalysisHistoryItem,
): Promise<void> {
  const existing = storage.get<AnalysisHistoryItem[]>('oopsie.analysisHistory', []);
  const history = Array.isArray(existing) ? existing : [];
  await storage.update('oopsie.analysisHistory', [item, ...history]);
}
