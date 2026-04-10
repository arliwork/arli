-- ARLI Production Database Schema

-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    principal VARCHAR(255) UNIQUE, -- ICP Principal
    wallet_address VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Agents
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    owner_id UUID REFERENCES users(id) ON DELETE CASCADE,
    creator_id UUID REFERENCES users(id),
    level INTEGER DEFAULT 1,
    tier VARCHAR(50) DEFAULT 'NOVICE',
    total_xp BIGINT DEFAULT 0,
    total_tasks INTEGER DEFAULT 0,
    successful_tasks INTEGER DEFAULT 0,
    total_revenue DECIMAL(18, 2) DEFAULT 0,
    market_value DECIMAL(18, 2) DEFAULT 50,
    hourly_rate DECIMAL(18, 2) DEFAULT 10,
    is_listed BOOLEAN DEFAULT FALSE,
    listing_price DECIMAL(18, 2),
    nft_token_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Agent Expertise
CREATE TABLE agent_expertise (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    domain VARCHAR(100) NOT NULL,
    tasks_completed INTEGER DEFAULT 0,
    successful_tasks INTEGER DEFAULT 0,
    total_revenue DECIMAL(18, 2) DEFAULT 0,
    avg_rating DECIMAL(3, 2),
    UNIQUE(agent_id, domain)
);

-- Tasks
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id VARCHAR(255) UNIQUE NOT NULL,
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    category VARCHAR(100) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending', -- pending, running, completed, failed
    success BOOLEAN,
    execution_time_seconds INTEGER,
    revenue_generated DECIMAL(18, 2) DEFAULT 0,
    client_rating INTEGER,
    result_data JSONB,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Skills
CREATE TABLE skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    price DECIMAL(18, 2) NOT NULL,
    author_id UUID REFERENCES users(id),
    code_package_url VARCHAR(500),
    version VARCHAR(50) DEFAULT '1.0.0',
    downloads INTEGER DEFAULT 0,
    rating DECIMAL(3, 2),
    review_count INTEGER DEFAULT 0,
    is_published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Skill Purchases
CREATE TABLE skill_purchases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id UUID REFERENCES skills(id),
    buyer_id UUID REFERENCES users(id),
    price_paid DECIMAL(18, 2),
    license_key VARCHAR(255),
    purchased_at TIMESTAMP DEFAULT NOW()
);

-- Agent Sales
CREATE TABLE agent_sales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES agents(id),
    seller_id UUID REFERENCES users(id),
    buyer_id UUID REFERENCES users(id),
    price DECIMAL(18, 2),
    platform_fee DECIMAL(18, 2),
    creator_royalty DECIMAL(18, 2),
    seller_receives DECIMAL(18, 2),
    sale_type VARCHAR(50), -- direct, auction
    tx_hash VARCHAR(255), -- blockchain tx
    sold_at TIMESTAMP DEFAULT NOW()
);

-- Reviews
CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES agents(id),
    reviewer_id UUID REFERENCES users(id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Achievements
CREATE TABLE achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    achievement_type VARCHAR(100) NOT NULL,
    unlocked_at TIMESTAMP DEFAULT NOW()
);

-- Wallet Transactions
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    type VARCHAR(50), -- deposit, withdrawal, purchase, sale
    amount DECIMAL(18, 2),
    currency VARCHAR(10) DEFAULT 'ICP',
    tx_hash VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Task Queue (для workers)
CREATE TABLE task_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id VARCHAR(255) UNIQUE NOT NULL,
    agent_id UUID REFERENCES agents(id),
    category VARCHAR(100),
    payload JSONB,
    priority INTEGER DEFAULT 1,
    status VARCHAR(50) DEFAULT 'queued',
    worker_id VARCHAR(255),
    attempts INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_agents_owner ON agents(owner_id);
CREATE INDEX idx_agents_listed ON agents(is_listed) WHERE is_listed = TRUE;
CREATE INDEX idx_tasks_agent ON tasks(agent_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_skills_published ON skills(is_published) WHERE is_published = TRUE;
CREATE INDEX idx_transactions_user ON transactions(user_id);
CREATE INDEX idx_task_queue_status ON task_queue(status);

-- Triggers для updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON agents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert demo users (только для теста, потом удалить)
INSERT INTO users (email, principal) VALUES 
    ('admin@arli.io', 'rdmx6-jaaaa-aaaaa-aaadq-cai');
