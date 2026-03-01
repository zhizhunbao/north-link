/**
 * Scraper usage API service.
 */
import { api } from "./api";
import type { ScraperUsage } from "../types/chat";

export const scraperService = {
  getUsage: () =>
    api.get<ScraperUsage>("/api/v1/scraper/usage").then((r) => r.data),
};
