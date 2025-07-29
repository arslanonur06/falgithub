-- Premium Plans and Payment System Setup for Fal Gram Bot
-- This file sets up the complete premium subscription and payment system

-- 1. Premium Plans Table
CREATE TABLE IF NOT EXISTS premium_plans (
    id SERIAL PRIMARY KEY,
    plan_id VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    name_en VARCHAR(100) NOT NULL,
    price INTEGER NOT NULL, -- Price in Telegram Stars
    price_stars INTEGER NOT NULL, -- Price in Telegram Stars (same as price)
    features JSONB NOT NULL, -- Turkish features
    features_en JSONB NOT NULL, -- English features
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. User Subscriptions Table
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id VARCHAR(20) NOT NULL REFERENCES premium_plans(plan_id),
    status VARCHAR(20) NOT NULL DEFAULT 'active', -- active, cancelled, expired
    start_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    end_date TIMESTAMP WITH TIME ZONE,
    payment_method VARCHAR(50) DEFAULT 'telegram_stars',
    total_paid INTEGER NOT NULL, -- Total amount paid in Telegram Stars
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Payment Transactions Table
CREATE TABLE IF NOT EXISTS payment_transactions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id VARCHAR(20) REFERENCES premium_plans(plan_id),
    transaction_id VARCHAR(100) UNIQUE NOT NULL,
    amount INTEGER NOT NULL, -- Amount in Telegram Stars
    currency VARCHAR(10) DEFAULT 'XTR',
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending, completed, failed, refunded
    payment_method VARCHAR(50) DEFAULT 'telegram_stars',
    telegram_payment_charge_id VARCHAR(100),
    telegram_payment_provider_charge_id VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Payment History Table (for individual service payments)
CREATE TABLE IF NOT EXISTS payment_history (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    service_type VARCHAR(50) NOT NULL, -- coffee_fortune, tarot, dream_analysis
    amount INTEGER NOT NULL, -- Amount in Telegram Stars
    transaction_id VARCHAR(100) UNIQUE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'completed',
    telegram_payment_charge_id VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Insert Default Premium Plans (CORRECTED PRICES)
INSERT INTO premium_plans (plan_id, name, name_en, price, price_stars, features, features_en) VALUES
('free', 'Ücretsiz', 'Free', 0, 0, 
 '["3 ücretsiz fal", "Temel astroloji", "Günlük burç"]',
 '["3 free readings", "Basic astrology", "Daily horoscope"]'),
('basic', 'Temel Plan', 'Basic Plan', 500, 500,
 '["Sınırsız fal", "Gelişmiş astroloji", "Haftalık raporlar", "Reklamsız deneyim"]',
 '["Unlimited readings", "Advanced astrology", "Weekly reports", "Ad-free experience"]'),
('premium', 'Premium Plan', 'Premium Plan', 1000, 1000,
 '["Tüm özellikler", "Ay takvimi", "Gezegen geçişleri", "Haftalık raporlar", "PDF raporları"]',
 '["All features", "Moon calendar", "Planetary transits", "Weekly reports", "PDF reports"]'),
('vip', 'VIP Plan', 'VIP Plan', 2000, 2000,
 '["Tüm özellikler", "7/24 Astroloji Chatbot", "Sosyal özellikler", "Öncelikli destek", "Kişisel danışman"]',
 '["All features", "24/7 Astrology Chatbot", "Social features", "Priority support", "Personal consultant"]')
ON CONFLICT (plan_id) DO UPDATE SET
    name = EXCLUDED.name,
    name_en = EXCLUDED.name_en,
    price = EXCLUDED.price,
    price_stars = EXCLUDED.price_stars,
    features = EXCLUDED.features,
    features_en = EXCLUDED.features_en,
    updated_at = NOW();

-- 6. Add premium_plan column to users table if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'premium_plan') THEN
        ALTER TABLE users ADD COLUMN premium_plan VARCHAR(20) DEFAULT 'free';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'premium_expires_at') THEN
        ALTER TABLE users ADD COLUMN premium_expires_at TIMESTAMP WITH TIME ZONE;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'total_spent') THEN
        ALTER TABLE users ADD COLUMN total_spent INTEGER DEFAULT 0;
    END IF;
END $$;

-- 7. Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user_id ON user_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_plan_id ON user_subscriptions(plan_id);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_status ON user_subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_payment_transactions_user_id ON payment_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_payment_transactions_status ON payment_transactions(status);
CREATE INDEX IF NOT EXISTS idx_payment_history_user_id ON payment_history(user_id);
CREATE INDEX IF NOT EXISTS idx_payment_history_service_type ON payment_history(service_type);

-- 8. Create functions for premium plan management

-- Function to get user's current premium plan
CREATE OR REPLACE FUNCTION get_user_premium_plan(user_id_param BIGINT)
RETURNS TABLE(
    plan_id VARCHAR(20),
    plan_name VARCHAR(100),
    plan_name_en VARCHAR(100),
    price INTEGER,
    is_active BOOLEAN,
    expires_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pp.plan_id,
        pp.name,
        pp.name_en,
        pp.price,
        us.status = 'active' as is_active,
        us.end_date as expires_at
    FROM premium_plans pp
    LEFT JOIN user_subscriptions us ON pp.plan_id = us.plan_id 
        AND us.user_id = user_id_param 
        AND us.status = 'active'
    WHERE pp.plan_id = COALESCE(us.plan_id, 'free')
    ORDER BY us.created_at DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Function to check if user has premium access
CREATE OR REPLACE FUNCTION has_premium_access(user_id_param BIGINT, required_plan VARCHAR(20) DEFAULT 'basic')
RETURNS BOOLEAN AS $$
DECLARE
    user_plan VARCHAR(20);
    plan_hierarchy JSONB := '{"free": 0, "basic": 1, "premium": 2, "vip": 3}'::JSONB;
BEGIN
    -- Get user's current plan
    SELECT u.premium_plan INTO user_plan
    FROM users u
    WHERE u.id = user_id_param;
    
    -- Check if user has active subscription
    IF EXISTS (
        SELECT 1 FROM user_subscriptions 
        WHERE user_id = user_id_param 
        AND status = 'active' 
        AND end_date > NOW()
    ) THEN
        -- Check plan hierarchy
        RETURN (plan_hierarchy->user_plan)::INTEGER >= (plan_hierarchy->required_plan)::INTEGER;
    END IF;
    
    RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

-- Function to record payment transaction
CREATE OR REPLACE FUNCTION record_payment_transaction(
    user_id_param BIGINT,
    plan_id_param VARCHAR(20),
    transaction_id_param VARCHAR(100),
    amount_param INTEGER,
    status_param VARCHAR(20) DEFAULT 'completed',
    telegram_charge_id VARCHAR(100) DEFAULT NULL
)
RETURNS INTEGER AS $$
DECLARE
    transaction_record_id INTEGER;
BEGIN
    -- Insert payment transaction
    INSERT INTO payment_transactions (
        user_id, plan_id, transaction_id, amount, status, 
        telegram_payment_charge_id
    ) VALUES (
        user_id_param, plan_id_param, transaction_id_param, amount_param, status_param,
        telegram_charge_id
    ) RETURNING id INTO transaction_record_id;
    
    -- Update user's total spent
    UPDATE users 
    SET total_spent = total_spent + amount_param
    WHERE id = user_id_param;
    
    -- If subscription payment, update user subscription
    IF plan_id_param IS NOT NULL AND plan_id_param != 'free' THEN
        INSERT INTO user_subscriptions (
            user_id, plan_id, status, end_date, total_paid
        ) VALUES (
            user_id_param, plan_id_param, 'active', 
            NOW() + INTERVAL '1 month', amount_param
        ) ON CONFLICT (user_id, plan_id) DO UPDATE SET
            status = 'active',
            end_date = NOW() + INTERVAL '1 month',
            total_paid = user_subscriptions.total_paid + amount_param,
            updated_at = NOW();
        
        -- Update user's premium plan
        UPDATE users 
        SET premium_plan = plan_id_param,
            premium_expires_at = NOW() + INTERVAL '1 month'
        WHERE id = user_id_param;
    END IF;
    
    RETURN transaction_record_id;
END;
$$ LANGUAGE plpgsql;

-- Function to record service payment (coffee, tarot, dream)
CREATE OR REPLACE FUNCTION record_service_payment(
    user_id_param BIGINT,
    service_type_param VARCHAR(50),
    amount_param INTEGER,
    transaction_id_param VARCHAR(100),
    telegram_charge_id VARCHAR(100) DEFAULT NULL
)
RETURNS INTEGER AS $$
DECLARE
    payment_record_id INTEGER;
BEGIN
    -- Insert payment history
    INSERT INTO payment_history (
        user_id, service_type, amount, transaction_id, telegram_payment_charge_id
    ) VALUES (
        user_id_param, service_type_param, amount_param, transaction_id_param, telegram_charge_id
    ) RETURNING id INTO payment_record_id;
    
    -- Update user's total spent
    UPDATE users 
    SET total_spent = total_spent + amount_param
    WHERE id = user_id_param;
    
    RETURN payment_record_id;
END;
$$ LANGUAGE plpgsql;

-- 9. Create views for easy data access

-- View for user premium status
CREATE OR REPLACE VIEW user_premium_status AS
SELECT 
    u.id as user_id,
    u.first_name,
    u.username,
    u.premium_plan,
    u.premium_expires_at,
    u.total_spent,
    CASE 
        WHEN u.premium_expires_at > NOW() THEN 'active'
        ELSE 'expired'
    END as subscription_status,
    pp.name as plan_name,
    pp.name_en as plan_name_en,
    pp.price as plan_price
FROM users u
LEFT JOIN premium_plans pp ON u.premium_plan = pp.plan_id;

-- View for payment statistics
CREATE OR REPLACE VIEW payment_statistics AS
SELECT 
    DATE_TRUNC('day', created_at) as payment_date,
    COUNT(*) as total_transactions,
    SUM(amount) as total_amount,
    COUNT(DISTINCT user_id) as unique_users
FROM payment_transactions 
WHERE status = 'completed'
GROUP BY DATE_TRUNC('day', created_at)
ORDER BY payment_date DESC;

-- 10. Insert sample data for testing (optional)
-- Uncomment the following lines if you want to add test data

/*
INSERT INTO payment_transactions (user_id, plan_id, transaction_id, amount, status) VALUES
(123456789, 'basic', 'test_txn_001', 500, 'completed'),
(123456789, 'premium', 'test_txn_002', 1000, 'completed');

INSERT INTO payment_history (user_id, service_type, amount, transaction_id) VALUES
(123456789, 'coffee_fortune', 250, 'test_service_001'),
(123456789, 'tarot', 250, 'test_service_002');
*/

-- 11. Create triggers for automatic updates

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_premium_plans_updated_at 
    BEFORE UPDATE ON premium_plans 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_subscriptions_updated_at 
    BEFORE UPDATE ON user_subscriptions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payment_transactions_updated_at 
    BEFORE UPDATE ON payment_transactions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 12. Permissions are handled by Supabase automatically
-- No additional grants needed for Supabase setup

-- 13. Final verification queries
-- Run these to verify the setup:

-- Check premium plans
-- SELECT * FROM premium_plans;

-- Check user premium status (replace with actual user_id)
-- SELECT * FROM user_premium_status WHERE user_id = 123456789;

-- Check payment statistics
-- SELECT * FROM payment_statistics LIMIT 10; 