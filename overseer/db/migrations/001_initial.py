from yoyo import step

steps = [
    step(
        """
        CREATE TABLE plugins (
            id VARCHAR(24) PRIMARY KEY,
            name VARCHAR(255) NOT NULL UNIQUE,
            version VARCHAR(50) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            manifest TEXT NOT NULL,
            image_name VARCHAR(255) NOT NULL,
            registry_url VARCHAR(255) NOT NULL,
            is_active BOOLEAN DEFAULT true
        )
        """,
        "DROP TABLE plugins"
    ),
    step(
        """
        ALTER TABLE deployments 
        ADD COLUMN plugin_id VARCHAR(24) REFERENCES plugins(id)
        """,
        "ALTER TABLE deployments DROP COLUMN plugin_id"
    )
] 