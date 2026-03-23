import Database from 'better-sqlite3';
import path from 'path';

let db: Database.Database;

export function getDb() {
  if (!db) {
    const dbPath = path.join(process.cwd(), 'data', 'brokerage.db');
    db = new Database(dbPath, { readonly: true, fileMustExist: true });
    // Define a busy timeout just in case
    db.pragma('busy_timeout = 3000');
  }
  return db;
}

export function executeQuery(sql: string) {
  const database = getDb();
  try {
    // Only allow read-only operations. better-sqlite3 throws on modifications when in readonly mode.
    const stmt = database.prepare(sql);
    
    // We enforce a hard limit to prevent giant payloads. 
    // Ideally this is done in SQL, but we slice the result array just in case as a fallback.
    const rows = stmt.all();
    return { success: true, rows: rows.slice(0, 1000) };
  } catch (error) {
    return { success: false, error: error instanceof Error ? error.message : String(error) };
  }
}
