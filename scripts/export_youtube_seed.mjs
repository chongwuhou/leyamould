import { VIDEO_SEED } from "../functions/_shared/youtube-videos.js";
import { writeFile } from "node:fs/promises";

await writeFile(new URL("../data/leya-youtube-seed.json", import.meta.url), JSON.stringify(VIDEO_SEED, null, 2) + "\n", "utf8");
