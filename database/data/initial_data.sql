# Constitutional Hash: cdd01ef066bc6cf2
-- Initial data for ACGS Research Papers Knowledge Base

-- Insert research categories
INSERT INTO categories (name, description) VALUES 
('Constitutional AI', 'Research on constitutional approaches to AI alignment and safety'),
('Reward Modeling', 'Studies on reward model training, evaluation, and optimization'),
('RLHF', 'Reinforcement Learning from Human Feedback techniques and methodologies'),
('Preference Learning', 'Research on learning from human preferences and comparative judgments'),
('AI Safety', 'General AI safety research and risk mitigation strategies'),
('Language Model Alignment', 'Alignment techniques specific to large language models'),
('Robustness', 'Research on model robustness, adversarial attacks, and defenses'),
('Evaluation', 'Methods and frameworks for evaluating AI systems'),
('Ethics', 'Ethical considerations in AI development and deployment'),
('Governance', 'AI governance, policy, and regulatory approaches'),
('Interpretability', 'Research on model interpretability and explainability'),
('Training Methods', 'Novel training approaches and optimization techniques'),
('Human-AI Interaction', 'Studies on human-AI collaboration and interaction patterns'),
('Multi-Agent Systems', 'Research on coordination and interaction between multiple AI agents'),
('Causal Reasoning', 'Causal inference and reasoning in AI systems');

-- Insert subcategories
INSERT INTO categories (name, description, parent_id) VALUES 
('DPO', 'Direct Preference Optimization methods', (SELECT id FROM categories WHERE name = 'Preference Learning')),
('PPO', 'Proximal Policy Optimization techniques', (SELECT id FROM categories WHERE name = 'RLHF')),
('Reward Hacking', 'Studies on reward hacking and gaming behaviors', (SELECT id FROM categories WHERE name = 'Reward Modeling')),
('Constitutional Methods', 'Specific constitutional AI implementation techniques', (SELECT id FROM categories WHERE name = 'Constitutional AI')),
('Benchmark Development', 'Creation and validation of evaluation benchmarks', (SELECT id FROM categories WHERE name = 'Evaluation')),
('Human Feedback Collection', 'Methods for collecting and processing human feedback', (SELECT id FROM categories WHERE name = 'RLHF')),
('Adversarial Robustness', 'Defense against adversarial attacks', (SELECT id FROM categories WHERE name = 'Robustness')),
('Distribution Shift', 'Handling out-of-distribution scenarios', (SELECT id FROM categories WHERE name = 'Robustness')),
('Mechanistic Interpretability', 'Understanding internal model mechanisms', (SELECT id FROM categories WHERE name = 'Interpretability')),
('Multi-Objective Optimization', 'Balancing multiple objectives in training', (SELECT id FROM categories WHERE name = 'Training Methods'));

-- Insert initial keywords
INSERT INTO keywords (keyword, category_id) VALUES 
-- Constitutional AI keywords
('constitutional ai', (SELECT id FROM categories WHERE name = 'Constitutional AI')),
('constitutional training', (SELECT id FROM categories WHERE name = 'Constitutional AI')),
('harmlessness', (SELECT id FROM categories WHERE name = 'Constitutional AI')),
('helpfulness', (SELECT id FROM categories WHERE name = 'Constitutional AI')),
('ai constitution', (SELECT id FROM categories WHERE name = 'Constitutional AI')),

-- Reward Modeling keywords
('reward modeling', (SELECT id FROM categories WHERE name = 'Reward Modeling')),
('reward function', (SELECT id FROM categories WHERE name = 'Reward Modeling')),
('reward optimization', (SELECT id FROM categories WHERE name = 'Reward Modeling')),
('reward hacking', (SELECT id FROM categories WHERE name = 'Reward Modeling')),
('reward misspecification', (SELECT id FROM categories WHERE name = 'Reward Modeling')),
('reward ensembles', (SELECT id FROM categories WHERE name = 'Reward Modeling')),

-- RLHF keywords
('rlhf', (SELECT id FROM categories WHERE name = 'RLHF')),
('reinforcement learning from human feedback', (SELECT id FROM categories WHERE name = 'RLHF')),
('human feedback', (SELECT id FROM categories WHERE name = 'RLHF')),
('ppo', (SELECT id FROM categories WHERE name = 'RLHF')),
('proximal policy optimization', (SELECT id FROM categories WHERE name = 'RLHF')),

-- Preference Learning keywords
('preference learning', (SELECT id FROM categories WHERE name = 'Preference Learning')),
('preference optimization', (SELECT id FROM categories WHERE name = 'Preference Learning')),
('dpo', (SELECT id FROM categories WHERE name = 'Preference Learning')),
('direct preference optimization', (SELECT id FROM categories WHERE name = 'Preference Learning')),
('preference data', (SELECT id FROM categories WHERE name = 'Preference Learning')),
('human preferences', (SELECT id FROM categories WHERE name = 'Preference Learning')),
('preference modeling', (SELECT id FROM categories WHERE name = 'Preference Learning')),

-- AI Safety keywords
('ai safety', (SELECT id FROM categories WHERE name = 'AI Safety')),
('alignment', (SELECT id FROM categories WHERE name = 'AI Safety')),
('safety evaluation', (SELECT id FROM categories WHERE name = 'AI Safety')),
('risk assessment', (SELECT id FROM categories WHERE name = 'AI Safety')),
('safety measures', (SELECT id FROM categories WHERE name = 'AI Safety')),

-- Language Model keywords
('language models', (SELECT id FROM categories WHERE name = 'Language Model Alignment')),
('large language models', (SELECT id FROM categories WHERE name = 'Language Model Alignment')),
('llm', (SELECT id FROM categories WHERE name = 'Language Model Alignment')),
('transformer', (SELECT id FROM categories WHERE name = 'Language Model Alignment')),
('fine-tuning', (SELECT id FROM categories WHERE name = 'Language Model Alignment')),
('instruction following', (SELECT id FROM categories WHERE name = 'Language Model Alignment')),

-- Robustness keywords
('robustness', (SELECT id FROM categories WHERE name = 'Robustness')),
('adversarial examples', (SELECT id FROM categories WHERE name = 'Robustness')),
('distribution shift', (SELECT id FROM categories WHERE name = 'Robustness')),
('out-of-distribution', (SELECT id FROM categories WHERE name = 'Robustness')),
('generalization', (SELECT id FROM categories WHERE name = 'Robustness')),

-- Evaluation keywords
('evaluation', (SELECT id FROM categories WHERE name = 'Evaluation')),
('benchmarks', (SELECT id FROM categories WHERE name = 'Evaluation')),
('metrics', (SELECT id FROM categories WHERE name = 'Evaluation')),
('human evaluation', (SELECT id FROM categories WHERE name = 'Evaluation')),
('automated evaluation', (SELECT id FROM categories WHERE name = 'Evaluation')),

-- Ethics keywords
('ai ethics', (SELECT id FROM categories WHERE name = 'Ethics')),
('fairness', (SELECT id FROM categories WHERE name = 'Ethics')),
('bias', (SELECT id FROM categories WHERE name = 'Ethics')),
('transparency', (SELECT id FROM categories WHERE name = 'Ethics')),
('accountability', (SELECT id FROM categories WHERE name = 'Ethics')),

-- Governance keywords
('ai governance', (SELECT id FROM categories WHERE name = 'Governance')),
('policy', (SELECT id FROM categories WHERE name = 'Governance')),
('regulation', (SELECT id FROM categories WHERE name = 'Governance')),
('standards', (SELECT id FROM categories WHERE name = 'Governance')),

-- Interpretability keywords
('interpretability', (SELECT id FROM categories WHERE name = 'Interpretability')),
('explainability', (SELECT id FROM categories WHERE name = 'Interpretability')),
('mechanistic interpretability', (SELECT id FROM categories WHERE name = 'Interpretability')),
('feature visualization', (SELECT id FROM categories WHERE name = 'Interpretability')),

-- Training Methods keywords
('training methods', (SELECT id FROM categories WHERE name = 'Training Methods')),
('optimization', (SELECT id FROM categories WHERE name = 'Training Methods')),
('learning algorithms', (SELECT id FROM categories WHERE name = 'Training Methods')),
('curriculum learning', (SELECT id FROM categories WHERE name = 'Training Methods')),
('multi-task learning', (SELECT id FROM categories WHERE name = 'Training Methods')),

-- Human-AI Interaction keywords
('human-ai interaction', (SELECT id FROM categories WHERE name = 'Human-AI Interaction')),
('human-in-the-loop', (SELECT id FROM categories WHERE name = 'Human-AI Interaction')),
('collaborative ai', (SELECT id FROM categories WHERE name = 'Human-AI Interaction')),
('user studies', (SELECT id FROM categories WHERE name = 'Human-AI Interaction')),

-- Multi-Agent keywords
('multi-agent', (SELECT id FROM categories WHERE name = 'Multi-Agent Systems')),
('agent coordination', (SELECT id FROM categories WHERE name = 'Multi-Agent Systems')),
('emergent behavior', (SELECT id FROM categories WHERE name = 'Multi-Agent Systems')),

-- Causal Reasoning keywords
('causal reasoning', (SELECT id FROM categories WHERE name = 'Causal Reasoning')),
('causal inference', (SELECT id FROM categories WHERE name = 'Causal Reasoning')),
('causal models', (SELECT id FROM categories WHERE name = 'Causal Reasoning')),
('counterfactuals', (SELECT id FROM categories WHERE name = 'Causal Reasoning'));

-- Create some initial collections
INSERT INTO collections (name, description, is_public, created_by) VALUES 
('Constitutional AI Fundamentals', 'Core papers on constitutional AI approaches', true, 'system'),
('RLHF Methods', 'Key papers on reinforcement learning from human feedback', true, 'system'),
('Preference Optimization', 'Papers on preference learning and optimization techniques', true, 'system'),
('AI Safety Evaluation', 'Important evaluation methods for AI safety', true, 'system'),
('Reward Modeling Research', 'Comprehensive collection on reward modeling', true, 'system'),
('ACGS Core References', 'Essential papers for ACGS development', true, 'system');

-- Refresh the search view
SELECT refresh_paper_search_view();
