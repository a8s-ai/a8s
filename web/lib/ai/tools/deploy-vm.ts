import { tool } from 'ai';
import { z } from 'zod';

export const deployVM = tool({
  description:
    'Deploy a virtual machine environment with specified tools and data',
  parameters: z.object({
    environment_type: z
      .string()
      .describe('Type of environment to deploy (e.g., "claude")'),
    tools: z
      .array(z.string())
      .default([])
      .describe('List of tools to include in the environment'),
    data: z
      .record(z.string())
      .default({})
      .describe('Data to pass to the environment'),
    requirement: z
      .string()
      .describe('The requirement or task for the agent to execute'),
    ttl_seconds: z
      .number()
      .optional()
      .default(3600)
      .describe('Time to live in seconds for the deployment'),
  }),
  execute: async ({
    environment_type,
    tools,
    data,
    requirement,
    ttl_seconds,
  }) => {
    const overseerEndpoint = process.env.OVERSEER_API_ENDPOINT;

    if (!overseerEndpoint) {
      throw new Error('Overseer agent is not configured');
    }

    const response = await fetch(`${overseerEndpoint}/deployments`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        environment_type,
        tools,
        data,
        requirement,
        ttl_seconds,
      }),
    });

    const deploymentData = await response.json();
    return deploymentData;
  },
});
