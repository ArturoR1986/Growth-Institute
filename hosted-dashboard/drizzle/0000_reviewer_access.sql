CREATE TABLE reviewer_sessions (token_hash TEXT PRIMARY KEY NOT NULL, expires_at INTEGER NOT NULL);
--> statement-breakpoint
CREATE INDEX reviewer_sessions_expiry ON reviewer_sessions (expires_at);
--> statement-breakpoint
CREATE TABLE reviewer_attempts (ip_hash TEXT PRIMARY KEY NOT NULL, attempts INTEGER NOT NULL, resets_at INTEGER NOT NULL);
--> statement-breakpoint
CREATE INDEX reviewer_attempts_reset ON reviewer_attempts (resets_at);
