import {
  customProvider,
  extractReasoningMiddleware,
  wrapLanguageModel,
} from 'ai';
import { anthropic } from '@ai-sdk/anthropic';
import { isTestEnvironment } from '../constants';
import {
  artifactModel,
  chatModel,
  reasoningModel,
  titleModel,
} from './models.test';

export const myProvider = isTestEnvironment
  ? customProvider({
      languageModels: {
        'chat-model': chatModel,
        'chat-model-reasoning': reasoningModel,
        'title-model': titleModel,
        'artifact-model': artifactModel,
      },
    })
  : (customProvider({
      languageModels: {
        // @ts-ignore - Suppressing version compatibility issues
        'chat-model': anthropic('claude-3-7-sonnet-20250219'),
        // @ts-ignore - Suppressing version compatibility issues
        'chat-model-reasoning': wrapLanguageModel({
          // @ts-ignore - Suppressing version compatibility issues
          model: anthropic('claude-3-7-sonnet-20250219'),
          middleware: extractReasoningMiddleware({ tagName: 'think' }),
        }),
        // @ts-ignore - Suppressing version compatibility issues
        'title-model': anthropic('claude-3-7-sonnet-20250219'),
        // @ts-ignore - Suppressing version compatibility issues
        'artifact-model': anthropic('claude-3-7-sonnet-20250219'),
      },
    }) as any);
