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
                agreement_accepted: false,
                agreement_timestamp: null
            },
            job_preferences: {
                keywords: [],
                excluded_keywords: [],
                locations: [],
                salary_min: null,
                salary_max: null,
                job_types: [],
                experience_levels: [],
                industries: [],
                company_size: [],
                remote_preference: 'any',
                visa_sponsorship: false,
                minimum_rating: 3.5
            },
            application_settings: {
                auto_apply: true,
                max_applications_per_day: 1,
                cover_letter_template: '',
                cv_path: '',
                apply_to_agencies: false,
                skip_assessment_required: true,
                minimum_job_age_days: 1,
                maximum_job_age_days: 7,
                preferred_application_times: []
            },
            filters: {
                excluded_companies: [],
                required_benefits: [],
                avoid_unpaid_trials: true,
                minimum_description_length: 100,
                require_salary_disclosed: false
            },
            smart_matching: {
                skill_weight: 0.4,
                location_weight: 0.2,
                salary_weight: 0.3,
                company_weight: 0.1,
                auto_learn_preferences: true
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
        excludedKeywordsText: '',
        locationsText: '',
        industriesText: '',
        excludedCompaniesText: '',
        requiredBenefitsText: '',
        preferredTimesText: '',
        
        // Initialization
        async init() {
            console.log('🚀 Initializing Seek Bot Dashboard');
            await this.loadConfig();
            await this.refreshStatus();
            await this.loadData();
            setInterval(() => this.refreshStatus(), 300000); // Refresh every 5 minutes
        },

        // Load current config from backend
        async loadConfig() {
            try {
                const res = await fetch('/api/config');
                const data = await res.json();
                this.config = data;

                // Convert arrays to text for form inputs
                this.keywordsText = this.config.job_preferences.keywords?.join(', ') || '';
                this.excludedKeywordsText = this.config.job_preferences.excluded_keywords?.join(', ') || '';
                this.locationsText = this.config.job_preferences.locations?.join(', ') || '';
                this.industriesText = this.config.job_preferences.industries?.join(', ') || '';
                this.excludedCompaniesText = this.config.filters?.excluded_companies?.join(', ') || '';
                this.requiredBenefitsText = this.config.filters?.required_benefits?.join(', ') || '';
                this.preferredTimesText = this.config.application_settings.preferred_application_times?.join(', ') || '';
            } catch (err) {
                console.error('❌ Failed to load config:', err);
            }
        },

        // Save config to backend
        async updateConfig() {
            this.savingConfig = true;
            try {
                // Parse text inputs back to arrays
                this.config.job_preferences.keywords = this.keywordsText.split(',').map(k => k.trim()).filter(Boolean);
                this.config.job_preferences.excluded_keywords = this.excludedKeywordsText.split(',').map(k => k.trim()).filter(Boolean);
                this.config.job_preferences.locations = this.locationsText.split(',').map(l => l.trim()).filter(Boolean);
                this.config.job_preferences.industries = this.industriesText.split(',').map(i => i.trim()).filter(Boolean);
                this.config.filters.excluded_companies = this.excludedCompaniesText.split(',').map(c => c.trim()).filter(Boolean);
                this.config.filters.required_benefits = this.requiredBenefitsText.split(',').map(b => b.trim()).filter(Boolean);
                this.config.application_settings.preferred_application_times = this.preferredTimesText.split(',').map(t => t.trim()).filter(Boolean);

                const payload = {
                    // User settings
                    agreement_accepted: this.config.user.agreement_accepted,
                    
                    // Job preferences
                    keywords: this.config.job_preferences.keywords,
                    excluded_keywords: this.config.job_preferences.excluded_keywords,
                    locations: this.config.job_preferences.locations,
                    salary_min: this.config.job_preferences.salary_min,
                    salary_max: this.config.job_preferences.salary_max,
                    job_types: this.config.job_preferences.job_types,
                    experience_levels: this.config.job_preferences.experience_levels,
                    industries: this.config.job_preferences.industries,
                    company_size: this.config.job_preferences.company_size,
                    remote_preference: this.config.job_preferences.remote_preference,
                    visa_sponsorship: this.config.job_preferences.visa_sponsorship,
                    minimum_rating: this.config.job_preferences.minimum_rating,
                    
                    // Application settings
                    auto_apply: this.config.application_settings.auto_apply,
                    max_applications_per_day: this.config.application_settings.max_applications_per_day,
                    cover_letter_template: this.config.application_settings.cover_letter_template,
                    cv_path: this.config.application_settings.cv_path,
                    apply_to_agencies: this.config.application_settings.apply_to_agencies,
                    skip_assessment_required: this.config.application_settings.skip_assessment_required,
                    minimum_job_age_days: this.config.application_settings.minimum_job_age_days,
                    maximum_job_age_days: this.config.application_settings.maximum_job_age_days,
                    preferred_application_times: this.config.application_settings.preferred_application_times,
                    
                    // Filters
                    excluded_companies: this.config.filters.excluded_companies,
                    required_benefits: this.config.filters.required_benefits,
                    avoid_unpaid_trials: this.config.filters.avoid_unpaid_trials,
                    minimum_description_length: this.config.filters.minimum_description_length,
                    require_salary_disclosed: this.config.filters.require_salary_disclosed,
                    
                    // Smart matching
                    skill_weight: this.config.smart_matching.skill_weight,
                    location_weight: this.config.smart_matching.location_weight,
                    salary_weight: this.config.smart_matching.salary_weight,
                    company_weight: this.config.smart_matching.company_weight,
                    auto_learn_preferences: this.config.smart_matching.auto_learn_preferences,
                    
                    // DeepSeek API
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
                await fetch(`/api/data?data_type=${type}`, { method: 'DELETE' });
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
        },

        // Additional helper methods for the UI
        toggleAdvanced: false,

        // Form validation
        validateConfig() {
            // Basic validation logic
            if (!this.config.user.agreement_accepted) {
                alert('Please accept the terms and conditions');
                return false;
            }
            if (this.config.job_preferences.keywords.length === 0) {
                alert('Please add at least one keyword');
                return false;
            }
            return true;
        },

        // Reset form to defaults
        resetForm() {
            if (confirm('Are you sure you want to reset all configuration?')) {
                this.loadConfig();
            }
        },

        // Test configuration
        async testConfig() {
            try {
                const res = await fetch('/api/test-config', { method: 'POST' });
                const result = await res.json();
                alert(result.message || 'Configuration test completed');
            } catch (err) {
                console.error('❌ Config test failed:', err);
                alert('Configuration test failed');
            }
        },

        // Export/Import functions (placeholder)
        exportConfig() {
            const dataStr = JSON.stringify(this.config, null, 2);
            const dataBlob = new Blob([dataStr], {type: 'application/json'});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'seek-bot-config.json';
            link.click();
        },

        importConfig() {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = '.json';
            input.onchange = (e) => {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        try {
                            const config = JSON.parse(e.target.result);
                            this.config = config;
                            this.updateConfig();
                        } catch (err) {
                            alert('Invalid configuration file');
                        }
                    };
                    reader.readAsText(file);
                }
            };
            input.click();
        },

        resetConfig() {
            if (confirm('This will reset all configuration to defaults. Continue?')) {
                fetch('/api/config/reset', { method: 'POST' })
                    .then(() => this.loadConfig())
                    .catch(err => console.error('Reset failed:', err));
            }
        },

        // Data filtering and computed properties
        get filteredJobs() {
            return this.jobs.filter(job => {
                if (this.jobsSearch && !job.title.toLowerCase().includes(this.jobsSearch.toLowerCase())) {
                    return false;
                }
                // Add more filtering logic based on jobsFilter
                return true;
            });
        },

        get filteredApplied() {
            return this.applied.filter(app => {
                if (this.appliedFilter === 'all') return true;
                return app.status === this.appliedFilter;
            });
        },

        get filteredLogs() {
            return this.logs.filter(log => {
                if (this.logLevel === 'all') return true;
                return log.level === this.logLevel;
            });
        },

        // Additional UI state
        jobsSearch: '',
        jobsFilter: 'all',
        appliedFilter: 'all',
        logLevel: 'all',

        // Computed stats
        get jobsToday() {
            const today = new Date().toDateString();
            return this.jobs.filter(job => new Date(job.posted_date).toDateString() === today).length;
        },

        get avgSalary() {
            const salaries = this.jobs.filter(job => job.salary).map(job => parseInt(job.salary.replace(/\D/g, '')));
            return salaries.length ? Math.round(salaries.reduce((a, b) => a + b, 0) / salaries.length) : 0;
        },

        get remoteJobs() {
            return this.jobs.filter(job => job.remote || job.location?.toLowerCase().includes('remote')).length;
        },

        get responseRate() {
            const responded = this.applied.filter(app => app.status !== 'pending').length;
            return this.applied.length ? Math.round((responded / this.applied.length) * 100) : 0;
        },

        get interviewCount() {
            return this.applied.filter(app => app.status === 'interview').length;
        },

        get appliedThisWeek() {
            const weekAgo = new Date();
            weekAgo.setDate(weekAgo.getDate() - 7);
            return this.applied.filter(app => new Date(app.applied_date) > weekAgo).length;
        },

        // Job actions
        viewJob(job) {
            window.open(job.url, '_blank');
        },

        async applyToJob(job) {
            try {
                const res = await fetch('/api/apply', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ job_id: job.id })
                });
                const result = await res.json();
                if (result.success) {
                    job.applied = true;
                    await this.loadData();
                }
            } catch (err) {
                console.error('❌ Failed to apply to job:', err);
            }
        },

        blacklistJob(job) {
            if (confirm(`Blacklist ${job.company}?`)) {
                // Add to excluded companies
                if (!this.config.filters.excluded_companies.includes(job.company)) {
                    this.config.filters.excluded_companies.push(job.company);
                    this.updateConfig();
                }
            }
        },

        // Bulk actions
        get selectedJobs() {
            return this.jobs.filter(job => job.selected);
        },

        selectAllJobs(event) {
            this.jobs.forEach(job => job.selected = event.target.checked);
        },

        async bulkApply() {
            for (const job of this.selectedJobs) {
                await this.applyToJob(job);
            }
        },

        bulkBlacklist() {
            if (confirm(`Blacklist ${this.selectedJobs.length} companies?`)) {
                this.selectedJobs.forEach(job => {
                    if (!this.config.filters.excluded_companies.includes(job.company)) {
                        this.config.filters.excluded_companies.push(job.company);
                    }
                });
                this.updateConfig();
            }
        },

        // Data export
        exportData(type) {
            let data;
            switch (type) {
                case 'jobs':
                    data = this.jobs;
                    break;
                case 'applied':
                    data = this.applied;
                    break;
                case 'logs':
                    data = this.logs;
                    break;
                default:
                    data = { jobs: this.jobs, applied: this.applied, logs: this.logs };
            }
            
            const dataStr = JSON.stringify(data, null, 2);
            const dataBlob = new Blob([dataStr], {type: 'application/json'});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `seek-bot-${type}-${new Date().toISOString().split('T')[0]}.json`;
            link.click();
        },

        refreshData() {
            this.loadData();
        },

        // Resume upload handler
        async handleResumeUpload(event) {
            const file = event.target.files[0];
            if (!file) return;

            // Validate file type
            const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
            if (!allowedTypes.includes(file.type)) {
                alert('Please upload a PDF, DOC, or DOCX file');
                event.target.value = '';
                return;
            }

            // Validate file size (max 5MB)
            if (file.size > 5 * 1024 * 1024) {
                alert('File size must be less than 5MB');
                event.target.value = '';
                return;
            }

            try {
                const formData = new FormData();
                formData.append('resume', file);

                const response = await fetch('/api/upload-resume', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();
                
                if (result.success) {
                    this.config.application_settings.resume_filename = result.filename;
                    this.config.application_settings.cv_path = result.filepath;
                    console.log('✅ Resume uploaded successfully:', result.filename);
                } else {
                    alert('Failed to upload resume: ' + (result.error || 'Unknown error'));
                    event.target.value = '';
                }
            } catch (error) {
                console.error('❌ Resume upload failed:', error);
                alert('Failed to upload resume. Please try again.');
                event.target.value = '';
            }
        },

        // Analytics placeholder
        analytics: {
            totalJobs: 0,
            jobsToday: 0,
            totalApplications: 0,
            successRate: 0,
            avgSalary: 0,
            salaryRange: '',
            responseRate: 0,
            avgResponseTime: '',
            topCompanies: []
        }
    }
}
