/**
 * 思考日志管理器
 * 管理和显示思考过程日志
 */

class ThoughtLogger {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.logs = [];
        this.maxLogs = 100; // 最多保留 100 条日志
        
        if (!this.container) {
            console.error('ThoughtLogger container not found:', containerId);
            return;
        }
        
        this.init();
    }

    init() {
        // 绑定清空按钮
        const clearBtn = document.getElementById('clear-logs');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clear());
        }
    }

    /**
     * 添加日志
     * @param {string} message - 日志内容
     * @param {string} type - 日志类型：info | thinking | success | warning | error | waiting
     */
    addLog(message, type = 'info') {
        const timestamp = this.getCurrentTime();
        const log = {
            id: Date.now(),
            timestamp,
            type,
            message
        };
        
        this.logs.push(log);
        
        // 限制日志数量
        if (this.logs.length > this.maxLogs) {
            this.logs.shift();
        }
        
        this.renderLog(log);
        this.autoScroll();
        
        console.log(`[ThoughtLogger] [${type}] ${message}`);
    }

    /**
     * 渲染单条日志
     * @param {object} log 
     */
    renderLog(log) {
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${log.type}`;
        logEntry.dataset.id = log.id;
        
        const icons = {
            info: 'ℹ️',
            thinking: '💭',
            success: '✅',
            warning: '⚠️',
            error: '❌',
            waiting: '⏳'
        };
        
        logEntry.innerHTML = `
            <span class="log-time">${log.timestamp}</span>
            <span class="log-icon">${icons[log.type] || icons.info}</span>
            <span class="log-message">${this.escapeHtml(log.message)}</span>
        `;
        
        this.container.appendChild(logEntry);
    }

    /**
     * 自动滚动到最新日志
     */
    autoScroll() {
        setTimeout(() => {
            this.container.scrollTop = this.container.scrollHeight;
        }, 50);
    }

    /**
     * 清空所有日志
     */
    clear() {
        this.logs = [];
        this.container.innerHTML = '';
        this.addLog('日志已清空', 'info');
    }

    /**
     * 获取当前时间字符串
     * @returns {string}
     */
    getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString('zh-CN', {
            hour12: false,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    }

    /**
     * HTML 转义
     * @param {string} text 
     * @returns {string}
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * 批量添加日志
     * @param {Array} logs 
     */
    addLogs(logs) {
        logs.forEach(log => {
            this.addLog(log.message, log.type);
        });
    }

    /**
     * 从 JSON 文件加载日志
     * @param {string} filePath 
     */
    async loadFromFile(filePath) {
        try {
            const response = await fetch(filePath);
            const logs = await response.json();
            this.logs = [];
            this.container.innerHTML = '';
            this.addLogs(logs);
        } catch (error) {
            console.error('Failed to load logs from file:', error);
        }
    }

    /**
     * 获取所有日志
     * @returns {Array}
     */
    getLogs() {
        return this.logs;
    }
}

// 导出为全局变量
window.ThoughtLogger = ThoughtLogger;
