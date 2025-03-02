import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_tables():
    commands = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY,
            name VARCHAR NOT NULL,
            email VARCHAR NOT NULL UNIQUE,
            recovery_token VARCHAR,
            country VARCHAR,
            language VARCHAR,
            firebase_uid VARCHAR,
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS plans (
            id UUID PRIMARY KEY,
            name VARCHAR NOT NULL,
            file_limit INTEGER,
            status VARCHAR,
            description VARCHAR,
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS periods (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR NOT NULL UNIQUE,
            months INTEGER NOT NULL,
            discount_percentage INTEGER DEFAULT 0,
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS plan_periods (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            plan_id UUID NOT NULL REFERENCES plans(id),
            period_id UUID NOT NULL REFERENCES periods(id),
            price NUMERIC NOT NULL,
            currency VARCHAR NOT NULL,
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS subscriptions (
            id UUID PRIMARY KEY,
            status VARCHAR NOT NULL,
            start_date TIMESTAMP,
            end_date TIMESTAMP,
            remaining_file_quota INTEGER,
            auto_renew BOOLEAN,
            plan_id UUID NOT NULL REFERENCES plans(id),
            user_id UUID NOT NULL REFERENCES users(id),
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS billings (
            id UUID PRIMARY KEY,
            amount VARCHAR NOT NULL,
            currency VARCHAR,
            payment_date VARCHAR,
            payment_method VARCHAR,
            payment_status VARCHAR,
            transaction_id VARCHAR,
            plan_id VARCHAR,
            user_id UUID REFERENCES users(id),
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS integrations (
            id UUID PRIMARY KEY,
            name VARCHAR NOT NULL,
            api_key VARCHAR,
            repository VARCHAR,
            repository_user VARCHAR,
            repository_token VARCHAR,
            repository_url VARCHAR,
            analyze_types VARCHAR,
            quality_level VARCHAR,
            user_id UUID REFERENCES users(id),
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ
        )
        """
    ]

    conn = None
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="postgres",
            host="localhost"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Create database if it doesn't exist
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'codehammer'")
        exists = cur.fetchone()
        if not exists:
            cur.execute('CREATE DATABASE codehammer')
        
        # Close connection to postgres database
        cur.close()
        conn.close()
        
        # Connect to codehammer database
        conn = psycopg2.connect(
            dbname="codehammer",
            user="postgres",
            password="postgres",
            host="localhost"
        )
        cur = conn.cursor()
        
        # Create tables
        for command in commands:
            cur.execute(command)
            
        # Create indexes
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);
            CREATE INDEX IF NOT EXISTS idx_subscriptions_plan_id ON subscriptions(plan_id);
            CREATE INDEX IF NOT EXISTS idx_billings_user_id ON billings(user_id);
            CREATE INDEX IF NOT EXISTS idx_integrations_user_id ON integrations(user_id);
            CREATE INDEX IF NOT EXISTS idx_plan_periods_plan_id ON plan_periods(plan_id);
            CREATE INDEX IF NOT EXISTS idx_plan_periods_period_id ON plan_periods(period_id);
        """)
            
        cur.close()
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    create_tables()
