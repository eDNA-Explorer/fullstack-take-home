import { router } from "../trpc";
import { samplesRouter } from "./samples";

export const appRouter = router({
  samples: samplesRouter,
});

export type AppRouter = typeof appRouter;
