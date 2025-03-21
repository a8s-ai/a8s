import { motion } from 'framer-motion';
import Link from 'next/link';

export const Overview = () => {
  return (
    <motion.div
      key="overview"
      className="max-w-3xl mx-auto md:mt-20"
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.98 }}
      transition={{ delay: 0.5 }}
    >
      <div className="rounded-xl p-6 flex flex-col gap-8 leading-relaxed text-center max-w-xl">
        <p className="text-4xl font-bold">
          Agent8s
        </p>
        <p>
          Agent8s is an{' '}
          <Link
            className="font-medium underline underline-offset-4"
            href="https://github.com/a8s-ai/a8s"
            target="_blank"
          >
            open source
          </Link>{' '}
          platform that enables interaction with AI agents through a chat interface while providing 
          access to remote desktop environments that agents can control. The system supports parallel 
          agent operations, state preservation, and direct user intervention.
        </p>
        <p>
          You can learn more about the Agent8s by visiting the{' '}
          <Link
            className="font-medium underline underline-offset-4"
            href="https://github.com/a8s-ai/a8s"
            target="_blank"
          >
            docs
          </Link>
          .
        </p>
      </div>
    </motion.div>
  );
};
