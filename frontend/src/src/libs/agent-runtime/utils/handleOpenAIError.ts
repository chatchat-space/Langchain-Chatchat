import OpenAI from 'openai';

import { AgentRuntimeErrorType } from '../error';

export const handleOpenAIError = (
  error: any,
): { RuntimeError?: 'AgentRuntimeError'; errorResult: any } => {
  let errorResult: any;

  // Check if the error is an OpenAI APIError
  if (error instanceof OpenAI.APIError) {
    // if error is definitely OpenAI APIError, there will be an error object
    if (error.error) {
      errorResult = error.error;
    }
    // Or if there is a cause, we use error cause
    // This often happened when there is a bug of the `openai` package.
    else if (error.cause) {
      errorResult = error.cause;
    }
    // if there is no other request error, the error object is a Response like object
    else {
      errorResult = { headers: error.headers, stack: error.stack, status: error.status };
    }

    return {
      errorResult,
    };
  } else {
    const err = error as Error;

    errorResult = { cause: err.cause, message: err.message, name: err.name, stack: err.stack };

    return {
      RuntimeError: AgentRuntimeErrorType.AgentRuntimeError,
      errorResult,
    };
  }
};
