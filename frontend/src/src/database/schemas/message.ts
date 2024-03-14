/* eslint-disable sort-keys-fix/sort-keys-fix  */
import { z } from 'zod';

const TranslateSchema = z.object({
  from: z.string().optional(),
  to: z.string(),
  content: z.string().optional(),
});

const PluginSchema = z.object({
  identifier: z.string(),
  arguments: z.string(),
  apiName: z.string(),
  type: z.enum(['default', 'markdown', 'standalone', 'builtin']).default('default'),
});

export const DB_MessageSchema = z.object({
  role: z.enum(['user', 'system', 'assistant', 'function']),
  content: z.string(),
  files: z.array(z.string()).optional(),
  favorite: z.number().int().min(0).max(1).optional(),
  error: z.any().optional(),

  plugin: PluginSchema.optional(),
  pluginState: z.any().optional(),
  fromModel: z.string().optional(),
  fromProvider: z.string().optional(),
  translate: TranslateSchema.optional().or(z.literal(false)),
  tts: z.any().optional(),

  traceId: z.string().optional(),
  observationId: z.string().optional(),

  // foreign keys
  parentId: z.string().optional(),
  quotaId: z.string().optional(),
  sessionId: z.string(),
  topicId: z.string().nullable().optional(),
});

export type DB_Message = z.infer<typeof DB_MessageSchema>;
