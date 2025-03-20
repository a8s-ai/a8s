'use client';

import { Server } from "lucide-react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "./ui/card";
import { Skeleton } from "./ui/skeleton";
import { Button } from "./ui/button";
import { BoxIcon } from "./icons";
import { useVMConnection } from "@/hooks/use-vm-connection";

// Define types for deployment requests and responses
export interface DeploymentRequest {
  environment_type: string;
  tools: string[];
  data: Record<string, string>;
  requirement: string;
  ttl_seconds?: number;
}

export interface DeploymentResponse {
  id: string;
  status: "provisioning" | "ready" | "failed" | string;
  environment_type: string;
  created_at: string;
  connection_details?: {
    host?: string;
    port?: string;
    protocol?: string;
    view_token?: string;
    access_token?: string;
    [key: string]: string | undefined;
  };
  message?: string;
}

// Component for displaying a deployment request (call state)
export function DeployVMRequest({ args }: { args: DeploymentRequest }) {
  return (
    <Card className="w-full border border-muted">
      <CardHeader className="p-4 pb-2">
        <div className="flex justify-between items-center">
          <CardTitle className="text-sm flex items-center gap-2">
            <Server className="size-3.5" />
            VM Deployment
          </CardTitle>
          <Button disabled className="bg-zinc-900 dark:bg-zinc-100 hover:bg-zinc-800 dark:hover:bg-zinc-200 text-zinc-50 dark:text-zinc-900 hidden md:flex py-1.5 px-2 h-fit md:h-[34px] order-4 md:ml-auto text-xs">
            <BoxIcon size={16} />
            Connect VM
          </Button>
        </div>
        <CardDescription>Preparing to deploy the environment...</CardDescription>
      </CardHeader>
      <CardContent className="p-4">
        <div className="text-sm">
            <strong>Requirement:</strong>
            <p className="mt-1 text-muted-foreground line-clamp-2">{args.requirement}</p>
        </div>
      </CardContent>
      <CardFooter className="border-t bg-muted/50 py-2 px-4">
        <div className="w-full flex justify-between items-center text-xs text-muted-foreground">
          <div>Initializing deployment...</div>
          <div>Environment: {args.environment_type}</div>
        </div>
      </CardFooter>
    </Card>
  );
}

// Component for displaying a deployment result
export function DeployVMResult({ result }: { result: DeploymentResponse }) {
  // Format the created_at timestamp
  const createdAt = new Date(result.created_at);
  const formattedDate = createdAt.toLocaleString();  
  
  const { setVMConnection } = useVMConnection();
  
  const handleConnectVM = () => {
    // Get button position for animation
    const button = document.querySelector('[data-connect-vm-button]');
    const rect = button?.getBoundingClientRect() || { top: 0, left: 0, width: 0, height: 0 };
    
    // Extract or construct VNC URL from connection details
    let vncUrl = '';
    
    if (result.connection_details) {
      // Try to get a direct VNC URL
      if (result.connection_details.vnc_url) {
        vncUrl = result.connection_details.vnc_url;
      } else if (result.connection_details.vncUrl) {
        vncUrl = result.connection_details.vncUrl;
      } else if (result.connection_details.view_url) {
        vncUrl = result.connection_details.view_url;
      } else if (result.connection_details.viewUrl) {
        vncUrl = result.connection_details.viewUrl;
      }
      // If no direct URL, try to construct from host and port
      else if (result.connection_details.host) {
        const protocol = result.connection_details.protocol === 'https' ? 'https' : 'http';
        const host = result.connection_details.host;
        const port = result.connection_details.port || '80';
        vncUrl = `${protocol}://${host}:${port}`;
      }
    }
    
    // Fallback to localhost:8080 if no URL could be determined
    if (!vncUrl) {
      vncUrl = 'http://localhost:8080/';
    }
    
    // Set VM connection state
    setVMConnection((current) => ({
      ...current,
      deploymentId: result.id,
      environmentType: result.environment_type,
      connectionDetails: result.connection_details || {},
      vncUrl,
      isVisible: true,
      status: 'connecting',
      boundingBox: {
        top: rect.top,
        left: rect.left,
        width: rect.width,
        height: rect.height,
      }
    }));
  };
  
  return (
    <Card className="w-full border border-muted">
      <CardHeader className="p-4 pb-2">
        <div className="flex justify-between items-start">
          <CardTitle className="text-sm flex items-center gap-2">
            <Server className="size-3.5" />
            VM Deployment
          </CardTitle>
          <Button 
            className="bg-zinc-900 dark:bg-zinc-100 hover:bg-zinc-800 dark:hover:bg-zinc-200 text-zinc-50 dark:text-zinc-900 hidden md:flex py-1.5 px-2 h-fit md:h-[34px] order-4 md:ml-auto text-xs"
            onClick={handleConnectVM}
            data-connect-vm-button
          >
            <BoxIcon size={16} />
            Connect VM
          </Button>
        </div>
        <CardDescription className="text-sm">
          {result.message || `Environment ${result.id} (${result.environment_type})`}
        </CardDescription>
      </CardHeader>
      <CardContent className="p-4">
        <div className="space-y-3 text-sm">
          <div className="grid grid-cols-2 gap-2">
            <div>
              <div className="text-muted-foreground text-xs">Environment</div>
              <div className="font-mono">{result.environment_type}</div>
            </div>
            <div>
              <div className="text-muted-foreground text-xs">Created</div>
              <div>{formattedDate}</div>
            </div>
          </div>
          
        </div>
      </CardContent>
      <CardFooter className="border-t bg-muted/50 py-2 px-4">
        <div className="w-full text-xs text-muted-foreground">
          Deployment ID: {result.id}
        </div>
      </CardFooter>
    </Card>
  );
}

// Main component that handles both states
export function DeployVM({ 
  deploymentRequest, 
  deploymentResponse 
}: { 
  deploymentRequest?: DeploymentRequest;
  deploymentResponse?: DeploymentResponse;
}) {
  if (deploymentResponse) {
    return <DeployVMResult result={deploymentResponse} />;
  }
  
  if (deploymentRequest) {
    return <DeployVMRequest args={deploymentRequest} />;
  }
  
  // Loading state
  return (
    <Card className="w-full border border-muted">
      <CardHeader className="pb-2">
        <div className="flex justify-between items-center">
          <Skeleton className="h-5 w-40" />
          <Skeleton className="h-5 w-24" />
        </div>
        <Skeleton className="h-4 w-60 mt-1" />
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-2/3" />
        </div>
      </CardContent>
      <CardFooter className="border-t py-2 px-6">
        <Skeleton className="h-4 w-full" />
      </CardFooter>
    </Card>
  );
} 