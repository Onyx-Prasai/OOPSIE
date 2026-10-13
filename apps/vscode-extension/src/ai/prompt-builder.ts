import { AnalysisContext } from '../types/oopsie';

export function buildRepairPrompt(ctx: Partial<AnalysisContext>): string {
  return `My VS Code project has this error:

${ctx.errorText ?? ''}

Project context:
- Framework: ${ctx.framework ?? 'Unknown'}
- File: ${ctx.filePath ?? 'Unknown'}
${ctx.selectedCode ? `- Related code:\n\`\`\`\n${ctx.selectedCode}\n\`\`\`` : ''}

Please identify the root cause and make the smallest possible fix.
Do not change unrelated files, redesign the UI, or remove existing features.
Explain every file you change and provide verification steps.`;
}
