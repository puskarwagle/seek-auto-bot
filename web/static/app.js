/**
 * Seek Bot Dashboard Frontend
 * Alpine.js application for bot control and monitoring
 */

function seekBot() {
    return {
        // State
        status: {
            running: false,
            current_task: 'idle',
            timestamp: '',
            jobs_found: 0,
            applications_sent: 0,
            errors: 0
        },
        
        config: {
            user: {
                email: '',
                password: '',
                agreement_accepted: false
            },
            job_preferences: {
                keywords: [],
                locations: [],
                salary_min: null,
                salary_max: null,
                job_types: [],
                experience_levels: []
            },
            application_settings: {
                auto_apply: true,
                max_applications_per_day: 20,
                cover_letter_template: '',
                cv_path: ''
            },
            deepseek_api: {
                api_key: '',
                enabled: false
            }
        },
        
        jobs: [],
        applied: [],
        logs: [],
        
        // UI State
        activeTab: 'jobs',
        startingBot: false,
        stoppingBot: false,
        savingConfig: false,
        
        // Form helpers
        keywordsText: '',
        locationsText: '',
        
        // Initialization
        async init() {
            console.log('🚀 Initializing Seek Bot Dashboard');
            await this.loadConfig();
            await this.refreshStatus();
            await this.loadData();
            setInterval(() => this.refreshStatus(), 10000); // Refresh every 10s
        },

        // Load current config from backend
        async loadConfig() {
            try {
                const res = await fetch('/api/config');
                const data = await res.json();
                this.config = data;

                // Convert keywords/locations to text
                this.keywordsText = this.config.job_preferences.keywords.join(', ');
                this.locationsText = this.config.job_preferences.locations.join(', ');
            } catch (err) {
                console.error('❌ Failed to load config:', err);
            }
        },

        // Save config to backend
        async updateConfig() {
            this.savingConfig = true;
            try {
                this.config.job_preferences.keywords = this.keywordsText.split(',').map(k => k.trim()).filter(Boolean);
                this.config.job_preferences.locations = this.locationsText.split(',').map(l => l.trim()).filter(Boolean);

                const payload = {
                    email: this.config.user.email,
                    password: this.config.user.password,
                    agreement_accepted: this.config.user.agreement_accepted,
                    keywords: this.config.job_preferences.keywords,
                    locations: this.config.job_preferences.locations,
                    salary_min: this.config.job_preferences.salary_min,
                    salary_max: this.config.job_preferences.salary_max,
                    job_types: this.config.job_preferences.job_types,
                    experience_levels: this.config.job_preferences.experience_levels,
                    auto_apply: this.config.application_settings.auto_apply,
                    max_applications_per_day: this.config.application_settings.max_applications_per_day,
                    cover_letter_template: this.config.application_settings.cover_letter_template,
                    cv_path: this.config.application_settings.cv_path,
                    deepseek_api_key: this.config.deepseek_api.api_key,
                    deepseek_enabled: this.config.deepseek_api.enabled
                };

                const res = await fetch('/api/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                const result = await res.json();
                console.log('✅ Config saved:', result);
            } catch (err) {
                console.error('❌ Failed to update config:', err);
            } finally {
                this.savingConfig = false;
            }
        },

        // Refresh bot status
        async refreshStatus() {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();
                this.status = data;
            } catch (err) {
                console.error('❌ Failed to fetch status:', err);
            }
        },

        // Load all persistent data
        async loadData() {
            try {
                const jobsRes = await fetch('/api/jobs');
                const jobsData = await jobsRes.json();
                this.jobs = jobsData.jobs || [];

                const appliedRes = await fetch('/api/applied');
                const appliedData = await appliedRes.json();
                this.applied = appliedData.applied || [];

                const logsRes = await fetch('/api/logs');
                const logsData = await logsRes.json();
                this.logs = logsData.logs || [];
            } catch (err) {
                console.error('❌ Failed to load data:', err);
            }
        },

        // Clear specific data
        async clearData(type) {
            try {
                await fetch(`/data?data_type=${type}`, { method: 'DELETE' });
                console.log(`🧹 Cleared ${type}`);
                await this.loadData();
            } catch (err) {
                console.error(`❌ Failed to clear ${type}:`, err);
            }
        },

        // Start the bot
        async startBot() {
            this.startingBot = true;
            try {
                const res = await fetch('/api/start', { method: 'POST' });
                const result = await res.json();
                console.log('🚀 Bot started:', result);
                await this.refreshStatus();
            } catch (err) {
                console.error('❌ Failed to start bot:', err);
            } finally {
                this.startingBot = false;
            }
        },

        // Stop the bot
        async stopBot() {
            this.stoppingBot = true;
            try {
                const res = await fetch('/api/stop', { method: 'POST' });
                const result = await res.json();
                console.log('⏹️ Bot stopped:', result);
                await this.refreshStatus();
            } catch (err) {
                console.error('❌ Failed to stop bot:', err);
            } finally {
                this.stoppingBot = false;
            }
        }
    }
}
