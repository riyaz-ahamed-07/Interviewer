import { readFileSync } from "node:fs";
import { neon } from "@neondatabase/serverless";

function loadEnvLocal() {
  const raw = readFileSync(new URL("../.env.local", import.meta.url), "utf8");
  for (const line of raw.split(/\r?\n/)) {
    const m = line.match(/^([A-Z0-9_]+)=(.*)$/);
    if (!m) continue;
    let v = m[2].trim();
    if (
      (v.startsWith('"') && v.endsWith('"')) ||
      (v.startsWith("'") && v.endsWith("'"))
    ) {
      v = v.slice(1, -1);
    }
    if (!process.env[m[1]]) process.env[m[1]] = v;
  }
}

loadEnvLocal();
const url = process.env.DATABASE_URL;
if (!url) {
  console.error("FAIL missing DATABASE_URL");
  process.exit(1);
}

const sql = neon(url);
const id = crypto.randomUUID();

const ping = await sql`select current_database() as db, now() as ts`;
console.log("ping", ping[0]);

await sql`
  insert into interview_sessions (
    id, mode, run_style, debug_difficulty, phase, phase_started_at
  ) values (
    ${id}::uuid, 'medium', 'practice', 'medium', 'intro', now()
  )
`;

await sql`
  insert into interview_messages (session_id, role, content, phase)
  values (${id}::uuid, 'assistant', 'Neon smoke test opening', 'intro')
`;

const rows = await sql`
  select s.id::text as id, s.phase, m.content
  from interview_sessions s
  join interview_messages m on m.session_id = s.id
  where s.id = ${id}::uuid
`;
console.log("roundtrip", rows[0]);

await sql`delete from interview_sessions where id = ${id}::uuid`;
console.log("OK neon http smoke passed");
