import { AnimatePresence, motion } from 'framer-motion';
import { memo, useState, useEffect, useMemo } from 'react';
import { useWindowSize } from 'usehooks-ts';
import { useVMConnection } from '@/hooks/use-vm-connection';
import { useSidebar } from './ui/sidebar';
import VNCViewer from './vnc-viewer';
import { isValidServiceUrl } from '@/lib/utils';

// VM Connection Close Button Component
export function VMConnectionCloseButton() {
  const { setVMConnection } = useVMConnection();

  return (
    <button
      type="button"
      onClick={() =>
        setVMConnection((current) => ({ ...current, isVisible: false }))
      }
      className="rounded-full p-2 hover:bg-muted transition-all"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        strokeWidth={1.5}
        stroke="currentColor"
        className="size-5"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M6 18L18 6M6 6l12 12"
        />
      </svg>
    </button>
  );
}

function PureVMConnection() {
  const { vmConnection } = useVMConnection();
  const { open: isSidebarOpen } = useSidebar();

  const { width: windowWidth, height: windowHeight } = useWindowSize();
  const isMobile = windowWidth ? windowWidth < 768 : false;

  // Extract service URL from VNC URL
  const { serviceUrl, errorMessage } = useMemo(() => {
    if (!vmConnection.vncUrl) {
      return {
        serviceUrl: null,
        errorMessage: 'No VNC URL provided. Please try connecting again.',
      };
    }

    // Since vncUrl is already in service URL format, just validate it
    if (!isValidServiceUrl(vmConnection.vncUrl)) {
      return {
        serviceUrl: null,
        errorMessage: 'Invalid service URL format. Expected format: service-name.namespace.svc.cluster.local',
      };
    }

    return {
      serviceUrl: vmConnection.vncUrl,
      errorMessage: '',
    };
  }, [vmConnection.vncUrl]);

  return (
    <AnimatePresence>
      {vmConnection.isVisible && (
        <motion.div
          data-testid="vm-connection"
          className="flex flex-row h-dvh w-dvw fixed top-0 left-0 z-50 bg-transparent"
          initial={{ opacity: 1 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0, transition: { delay: 0.4 } }}
        >
          {!isMobile && (
            <motion.div
              className="fixed bg-background h-dvh"
              initial={{
                width: isSidebarOpen ? windowWidth - 256 : windowWidth,
                right: 0,
              }}
              animate={{ width: windowWidth, right: 0 }}
              exit={{
                width: isSidebarOpen ? windowWidth - 256 : windowWidth,
                right: 0,
              }}
            />
          )}

          <motion.div
            className="fixed dark:bg-muted bg-background h-dvh flex flex-col overflow-y-scroll md:border-l dark:border-zinc-700 border-zinc-200"
            initial={
              isMobile
                ? {
                    opacity: 1,
                    x: vmConnection.boundingBox.left,
                    y: vmConnection.boundingBox.top,
                    height: vmConnection.boundingBox.height,
                    width: vmConnection.boundingBox.width,
                    borderRadius: 50,
                  }
                : {
                    opacity: 1,
                    x: vmConnection.boundingBox.left,
                    y: vmConnection.boundingBox.top,
                    height: vmConnection.boundingBox.height,
                    width: vmConnection.boundingBox.width,
                    borderRadius: 50,
                  }
            }
            animate={
              isMobile
                ? {
                    opacity: 1,
                    x: 0,
                    y: 0,
                    height: windowHeight,
                    width: windowWidth ? windowWidth : 'calc(100dvw)',
                    borderRadius: 0,
                    transition: {
                      delay: 0,
                      type: 'spring',
                      stiffness: 200,
                      damping: 30,
                      duration: 5000,
                    },
                  }
                : {
                    opacity: 1,
                    x: 0,
                    y: 0,
                    height: windowHeight,
                    width: windowWidth,
                    borderRadius: 0,
                    transition: {
                      delay: 0,
                      type: 'spring',
                      stiffness: 200,
                      damping: 30,
                      duration: 5000,
                    },
                  }
            }
            exit={{
              opacity: 0,
              scale: 0.5,
              transition: {
                delay: 0.1,
                type: 'spring',
                stiffness: 600,
                damping: 30,
              },
            }}
          >
            <div className="p-2 flex flex-row justify-between items-start">
              <div className="flex flex-row gap-4 items-start">
                <VMConnectionCloseButton />

                <div className="flex flex-col">
                  <div className="font-medium capitalize">
                    {vmConnection.environmentType} Deployment
                  </div>
                  <div className="text-sm text-muted-foreground">
                    ID: {vmConnection.deploymentId}
                  </div>
                </div>
              </div>
            </div>

            <div className="dark:bg-muted bg-background h-full overflow-hidden !max-w-full relative flex items-center justify-center">
              {!serviceUrl && (
                <div className="absolute inset-0 flex items-center justify-center bg-background/80 z-10">
                  <div className="flex flex-col items-center gap-2 max-w-md text-center p-4">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      strokeWidth={1.5}
                      stroke="currentColor"
                      className="size-8 text-destructive"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"
                      />
                    </svg>
                    <div className="text-base font-medium">
                      Failed to load VM interface
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {errorMessage}
                    </div>
                  </div>
                </div>
              )}

              {serviceUrl && (
                <VNCViewer
                  serviceUrl={serviceUrl}
                  styles={{
                    container: {
                      width: '100%',
                      height: '100%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    },
                    screen: {
                      width: '100%',
                      height: '100%',
                      maxWidth: '100%',
                      maxHeight: '100%',
                    },
                    error: {
                      position: 'absolute',
                      inset: 0,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      backgroundColor: 'var(--background)',
                      padding: '1rem',
                    },
                    loading: {
                      position: 'absolute',
                      inset: 0,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      backgroundColor: 'var(--background)',
                      padding: '1rem',
                    },
                  }}
                />
              )}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export const VMConnection = memo(PureVMConnection);
